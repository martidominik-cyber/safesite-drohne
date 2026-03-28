"""
SafeSite Drohne – Datenbank-Schicht
Abstrahiert alle Datenzugriffe. Aktuell JSON-basiert.
→ Kann später durch Supabase/PostgreSQL ersetzt werden,
  ohne den restlichen Code zu ändern.

WICHTIG für Streamlit Community Cloud:
  JSON-Dateien im db_data/ Ordner werden bei jedem Redeploy
  zurückgesetzt! Für Produktionsbetrieb muss auf eine externe
  Datenbank (z.B. Supabase Free Tier) migriert werden.
"""
import json
import os
import uuid
import threading
from datetime import date
from typing import Optional, Tuple

from config import USER_DB, CUSTOMERS_DB, GEFAHRSTOFF_DB, NOTFALL_DB
from auth import hash_password, verify_password, needs_rehash

# Thread-Lock für gleichzeitige Schreibzugriffe
_lock = threading.Lock()


# ============================================================
# GENERISCHE JSON-HELFER
# ============================================================
def _read_json(path: str, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        _write_json(path, default)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _write_json(path: str, data):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def new_id() -> str:
    return str(uuid.uuid4())[:8]


# ============================================================
# BENUTZER (Login-Daten)
# ============================================================
def get_users() -> dict:
    """Gibt {username: hashed_password} zurück."""
    users = _read_json(USER_DB, {"admin": hash_password("1234")})
    # Migration: Falls Admin noch Klartext hat
    if "admin" in users and needs_rehash(users["admin"]):
        users["admin"] = hash_password(users["admin"])
        _write_json(USER_DB, users)
    return users


def save_users(users: dict):
    _write_json(USER_DB, users)


def create_login(username: str, password: str):
    """Erstellt einen neuen Login-Eintrag mit gehashtem Passwort."""
    users = get_users()
    users[username] = hash_password(password)
    save_users(users)


def check_login(username: str, password: str) -> bool:
    """Prüft Login-Daten. Rehashed alte Klartext-Passwörter automatisch."""
    users = get_users()
    if username not in users:
        return False
    stored = users[username]
    if not verify_password(password, stored):
        return False
    # Auto-Migration: Klartext → Hash
    if needs_rehash(stored):
        users[username] = hash_password(password)
        save_users(users)
    return True


def change_password(username: str, new_password: str):
    """Ändert das Passwort eines Benutzers."""
    users = get_users()
    if username in users:
        users[username] = hash_password(new_password)
        save_users(users)


def delete_login(username: str):
    """Löscht einen Login-Eintrag."""
    users = get_users()
    if username in users:
        del users[username]
        save_users(users)


# ============================================================
# KUNDEN
# ============================================================
def get_customers() -> dict:
    return _read_json(CUSTOMERS_DB, {})


def save_customers(customers: dict):
    _write_json(CUSTOMERS_DB, customers)


def find_customer(username_or_email: str) -> Tuple[Optional[str], Optional[dict]]:
    """Findet Kunden anhand Email ODER Benutzername."""
    customers = get_customers()
    for kid, data in customers.items():
        if data.get("email") == username_or_email:
            return kid, data
        if data.get("username") and data.get("username") == username_or_email:
            return kid, data
    return None, None


def get_credits(username_or_email: str) -> int:
    """Gibt verfügbare Credits zurück (0 falls nicht gefunden)."""
    _, data = find_customer(username_or_email)
    if data:
        return int(data.get("credits", 0))
    return 0


def deduct_credit(username_or_email: str) -> bool:
    """Zieht 1 Credit ab. Gibt True zurück bei Erfolg."""
    customers = get_customers()
    kid, data = find_customer(username_or_email)
    if kid and data and int(data.get("credits", 0)) > 0:
        customers[kid]["credits"] = int(data["credits"]) - 1
        save_customers(customers)
        return True
    return False


def update_credits(kunde_id: str, credits: int):
    """Setzt Credits eines Kunden."""
    customers = get_customers()
    if kunde_id in customers:
        customers[kunde_id]["credits"] = int(credits)
        save_customers(customers)


def create_customer(name: str, firma: str, email: str,
                    username: str = "", telefon: str = "",
                    adresse: str = "", credits: int = 0) -> str:
    """Erstellt neuen Kunden. Gibt die Kunden-ID zurück."""
    customers = get_customers()
    kid = new_id()
    customers[kid] = {
        "name": name,
        "firma": firma,
        "email": email,
        "username": username,
        "telefon": telefon,
        "adresse": adresse,
        "credits": credits,
        "erstellt_am": date.today().strftime("%d.%m.%Y"),
    }
    save_customers(customers)
    return kid


def update_customer(kunde_id: str, **kwargs):
    """Aktualisiert Kundenfelder."""
    customers = get_customers()
    if kunde_id in customers:
        for key, val in kwargs.items():
            customers[kunde_id][key] = val
        save_customers(customers)


def delete_customer(kunde_id: str):
    """Löscht einen Kunden und seine Login-Daten."""
    customers = get_customers()
    if kunde_id not in customers:
        return
    data = customers[kunde_id]
    # Logins entfernen
    if data.get("email"):
        delete_login(data["email"])
    if data.get("username"):
        delete_login(data["username"])
    del customers[kunde_id]
    save_customers(customers)


# ============================================================
# NOTFALLKONTAKTE
# ============================================================
def _default_notfall() -> dict:
    """Standard-Notfallnummern für die Schweiz."""
    return {
        "std_144":  {"name": "144 – Sanitätsnotruf", "desc": "Wichtigste Nummer bei medizinischen Notfällen:\n- Unfall\n- Herzinfarkt\n- Sturz", "tel": "144", "icon": "🚑", "owner": "all"},
        "std_1414": {"name": "1414 – Rega (Luftrettung)", "desc": "Bei schwer zugänglichem Gelände, Kran-Unfällen oder wenn Bodenambulanz zu lange braucht.", "tel": "1414", "icon": "🚁", "owner": "all"},
        "std_118":  {"name": "118 – Feuerwehr", "desc": "Nicht nur bei Feuer! Auch bei:\n- Personenrettung\n- Chemieunfällen\n- Verschüttungen", "tel": "118", "icon": "🚒", "owner": "all"},
        "std_145":  {"name": "145 – Tox Info Suisse", "desc": "Bei Vergiftungen oder Unfällen mit Chemikalien/Baustoffen.", "tel": "145", "icon": "☠️", "owner": "all"},
        "std_117":  {"name": "117 – Polizei", "desc": "Bei Verkehrsunfällen, Einbruch, Gewaltandrohung.", "tel": "117", "icon": "👮", "owner": "all"},
        "std_112":  {"name": "112 – Euro-Notruf", "desc": "Funktioniert oft auch ohne eigenes Handynetz (Roaming über Fremdnetze).", "tel": "112", "icon": "🌍", "owner": "all"},
    }


def get_notfall() -> dict:
    data = _read_json(NOTFALL_DB, None)
    if data is None or not data:
        data = _default_notfall()
        _write_json(NOTFALL_DB, data)
    return data


def save_notfall(data: dict):
    _write_json(NOTFALL_DB, data)


def add_notfall(name: str, tel: str, desc: str, icon: str, owner: str) -> str:
    data = get_notfall()
    nid = new_id()
    data[nid] = {"name": name, "tel": tel, "desc": desc, "icon": icon, "owner": owner}
    save_notfall(data)
    return nid


def delete_notfall(nid: str):
    data = get_notfall()
    if nid in data:
        del data[nid]
        save_notfall(data)


# ============================================================
# GEFAHRSTOFFKATASTER
# ============================================================
def _default_gefahrstoffe() -> dict:
    """6 Standard-Gefahrstoffe für den Bau."""
    stoffe = {}
    defaults = [
        {
            "name": "Zementhaltige Produkte",
            "handelsbezeichnung": "Beton, Mörtel, Fugenmassen",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "Zementhaltige Produkte",
            "ghs_symbole": "GHS05, GHS07",
            "gefahrenbeschreibung": "Ätzend / Reizend. Verursacht schwere Augenschäden. Hautreizungen (Maurerkrätze). Staub reizt Atemwege.",
            "schutzmassnahmen": "Handschuhe (Nitril/Butyl), Schutzbrille, lange Kleidung. Bei Staubentwicklung: Maske FFP2.",
            "lagerort": "Baustelle / Lager",
            "verwendung": "Bauarbeiten mit Beton, Mörtel und Fugenmassen",
        },
        {
            "name": "Lösungsmittelhaltige Farben/Lacke/Kleber",
            "handelsbezeichnung": "Verdünner, Kunstharzlacke",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "Lösungsmittelhaltige Farben/Lacke/Kleber",
            "ghs_symbole": "GHS02, GHS08, GHS07",
            "gefahrenbeschreibung": "Entzündbar / Gesundheitsschädlich. Dämpfe können Benommenheit verursachen. Kann Organe schädigen.",
            "schutzmassnahmen": "Gute Lüftung. Zündquellen fernhalten. Atemschutzmaske (Filter Typ A).",
            "lagerort": "Giftschrank / Lager",
            "verwendung": "Lackieren, Kleben mit lösungsmittelhaltigen Produkten",
        },
        {
            "name": "Epoxidharze (2-Komponenten)",
            "handelsbezeichnung": "Bodenbeschichtung, Injektionsmörtel",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "Epoxidharze (2-Komponenten)",
            "ghs_symbole": "GHS09, GHS05, GHS07",
            "gefahrenbeschreibung": "Sensibilisierend / Gewässergefährdend. Starke allergische Hautreaktionen möglich.",
            "schutzmassnahmen": "Hautkontakt strikt vermeiden! Lange Ärmel, Nitril-Handschuhe (dick), Schutzbrille.",
            "lagerort": "Giftschrank / Lager",
            "verwendung": "Bodenbeschichtungen, Injektionsarbeiten",
        },
        {
            "name": "PU-Produkte (Isocyanate)",
            "handelsbezeichnung": "Bauschaum, Montageschaum, PU-Kleber",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "PU-Produkte (Isocyanate)",
            "ghs_symbole": "GHS08, GHS07, GHS02",
            "gefahrenbeschreibung": "Krebserzeugungsverdacht / Atemwegssensibilisierend. Kann Allergien/Asthma auslösen.",
            "schutzmassnahmen": "Gute Lüftung. Schutzhandschuhe. Bei schlechter Lüftung Atemschutz.",
            "lagerort": "Giftschrank / Lager",
            "verwendung": "Montagearbeiten, Dichtungsarbeiten, Kleben",
        },
        {
            "name": "Kraftstoffe & Schmiermittel",
            "handelsbezeichnung": "Diesel, Benzin, Schalöl",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "Kraftstoffe & Schmiermittel",
            "ghs_symbole": "GHS02, GHS08, GHS09",
            "gefahrenbeschreibung": "Entzündbar / Aspirationsgefahr. Umweltgefährlich.",
            "schutzmassnahmen": "Auffangwannen nutzen. Feuerlöscher bereitstellen. Nicht rauchen.",
            "lagerort": "Tankstelle / Auffangwanne",
            "verwendung": "Betankung von Maschinen, Schalung",
        },
        {
            "name": "Reinigungsmittel (Sauer)",
            "handelsbezeichnung": "Zementschleierentferner, Sanitärreiniger",
            "hersteller": "Verschiedene Hersteller",
            "kategorie": "Reinigungsmittel (Sauer)",
            "ghs_symbole": "GHS05",
            "gefahrenbeschreibung": "Korrosiv / Ätzend. Verursacht schwere Verätzungen.",
            "schutzmassnahmen": "Schutzbrille (Korbbrille) zwingend. Säurebeständige Handschuhe.",
            "lagerort": "Giftschrank / Lager",
            "verwendung": "Reinigung von Zementschleiern, Sanitärreinigung",
        },
    ]
    for item in defaults:
        stoffe[new_id()] = {
            **item,
            "cas_nummer": "",
            "menge": "Variabel",
            "sdb_datum": "",
            "betriebsanweisung_vorhanden": "Ja",
            "substitution": "",
            "sdb_link": "",
            "sdb_datei": "",
            "owner": "all",
            "erstellt_am": date.today().strftime("%d.%m.%Y"),
        }
    return stoffe


def get_gefahrstoffe() -> dict:
    data = _read_json(GEFAHRSTOFF_DB, None)
    if data is None or not data:
        data = _default_gefahrstoffe()
        _write_json(GEFAHRSTOFF_DB, data)
    return data


def save_gefahrstoffe(data: dict):
    _write_json(GEFAHRSTOFF_DB, data)


def add_gefahrstoff(owner: str = "all", **kwargs) -> str:
    data = get_gefahrstoffe()
    gid = new_id()
    data[gid] = {
        **kwargs,
        "owner": owner,
        "erstellt_am": date.today().strftime("%d.%m.%Y"),
    }
    save_gefahrstoffe(data)
    return gid


def delete_gefahrstoff(gid: str):
    data = get_gefahrstoffe()
    if gid in data:
        del data[gid]
        save_gefahrstoffe(data)


# ============================================================
# MIGRATION: Alte users.json (Klartext) → Gehashte Passwörter
# ============================================================
def migrate_legacy_data():
    """
    Einmalige Migration:
    1. Alte users.json mit Klartext-Passwörtern → gehashte Passwörter
    2. Alte users.json mit verschachtelten Dicts → customers.json + flache users.json
    """
    if not os.path.exists(USER_DB):
        return

    try:
        with open(USER_DB, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return

    # Fall 1: Verschachtelte User-Daten (alt)
    has_nested = any(isinstance(v, dict) for v in raw.values())
    if has_nested:
        customers = get_customers()
        existing_emails = {c.get("email", "") for c in customers.values()}
        new_users = {}
        for username, data in raw.items():
            if isinstance(data, dict):
                pwd = data.get("password", "1234")
                new_users[username] = hash_password(pwd)
                email = data.get("email", f"{username}@example.com")
                if username != "admin" and email not in existing_emails:
                    kid = new_id()
                    customers[kid] = {
                        "name": data.get("name", username),
                        "firma": data.get("firma", ""),
                        "email": email,
                        "username": username,
                        "telefon": data.get("telefon", ""),
                        "adresse": data.get("adresse", ""),
                        "credits": data.get("credits", 0),
                        "erstellt_am": date.today().strftime("%d.%m.%Y"),
                    }
            else:
                # Klartext-Passwort → Hash
                new_users[username] = hash_password(data) if needs_rehash(data) else data
        save_users(new_users)
        save_customers(customers)
        return

    # Fall 2: Flache users.json, aber evtl. noch Klartext
    changed = False
    for username, pwd in raw.items():
        if needs_rehash(pwd):
            raw[username] = hash_password(pwd)
            changed = True
    if changed:
        save_users(raw)
