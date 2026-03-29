"""
SafeSite Drohne – Datenbank-Schicht (Supabase)
================================================
Ersetzt die alte JSON-basierte Datenbank.
Gleiche Funktionsnamen → restlicher Code bleibt unverändert.

Supabase Free Tier:
  - 500 MB Datenbank
  - 50'000 API-Aufrufe/Monat
  - Daten gehen NIE verloren (auch nicht bei Redeploy!)
"""
import streamlit as st
from datetime import date
from typing import Optional, Tuple
from supabase import create_client, Client

from auth import hash_password, verify_password, needs_rehash


# ============================================================
# SUPABASE CLIENT
# ============================================================
@st.cache_resource
def _get_client() -> Client:
    """Erstellt einen Supabase-Client (wird gecacht)."""
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ SUPABASE_URL und SUPABASE_KEY fehlen in den Secrets!")
        st.stop()
    return create_client(url, key)


def _db() -> Client:
    return _get_client()


# ============================================================
# BENUTZER (Login-Daten)
# ============================================================
def get_users() -> dict:
    """Gibt {username: password_hash} zurück."""
    res = _db().table("users").select("username, password_hash").execute()
    users = {}
    for row in res.data:
        users[row["username"]] = row["password_hash"]
    # Sicherstellen dass Admin existiert
    if "admin" not in users:
        hashed = hash_password("1234")
        _db().table("users").insert({"username": "admin", "password_hash": hashed}).execute()
        users["admin"] = hashed
    return users


def save_users(users: dict):
    """Überschreibt alle User-Einträge (für Migration)."""
    for username, pwd_hash in users.items():
        existing = _db().table("users").select("id").eq("username", username).execute()
        if existing.data:
            _db().table("users").update({"password_hash": pwd_hash}).eq("username", username).execute()
        else:
            _db().table("users").insert({"username": username, "password_hash": pwd_hash}).execute()


def create_login(username: str, password: str):
    """Erstellt einen neuen Login-Eintrag."""
    hashed = hash_password(password)
    existing = _db().table("users").select("id").eq("username", username).execute()
    if existing.data:
        _db().table("users").update({"password_hash": hashed}).eq("username", username).execute()
    else:
        _db().table("users").insert({"username": username, "password_hash": hashed}).execute()


def check_login(username: str, password: str) -> bool:
    """Prüft Login. Rehashed alte Klartext-Passwörter automatisch."""
    res = _db().table("users").select("password_hash").eq("username", username).execute()
    if not res.data:
        return False
    stored = res.data[0]["password_hash"]
    if not verify_password(password, stored):
        return False
    # Auto-Migration: Klartext → Hash
    if needs_rehash(stored):
        hashed = hash_password(password)
        _db().table("users").update({"password_hash": hashed}).eq("username", username).execute()
    return True


def change_password(username: str, new_password: str):
    """Ändert das Passwort."""
    hashed = hash_password(new_password)
    _db().table("users").update({"password_hash": hashed}).eq("username", username).execute()


def delete_login(username: str):
    """Löscht einen Login-Eintrag."""
    _db().table("users").delete().eq("username", username).execute()


# ============================================================
# KUNDEN
# ============================================================
def get_customers() -> dict:
    """Gibt {id: {name, firma, email, ...}} zurück."""
    res = _db().table("customers").select("*").execute()
    customers = {}
    for row in res.data:
        kid = str(row["id"])
        customers[kid] = {
            "name": row.get("name", ""),
            "firma": row.get("firma", ""),
            "email": row.get("email", ""),
            "username": row.get("username", ""),
            "telefon": row.get("telefon", ""),
            "adresse": row.get("adresse", ""),
            "credits": int(row.get("credits", 0)),
            "erstellt_am": row.get("erstellt_am", ""),
        }
    return customers


def save_customers(customers: dict):
    """Speichert alle Kunden (für Bulk-Updates)."""
    for kid, data in customers.items():
        existing = _db().table("customers").select("id").eq("id", kid).execute()
        if existing.data:
            _db().table("customers").update(data).eq("id", kid).execute()


def find_customer(username_or_email: str) -> Tuple[Optional[str], Optional[dict]]:
    """Findet Kunden anhand Email ODER Benutzername."""
    # Suche nach Email
    res = _db().table("customers").select("*").eq("email", username_or_email).execute()
    if res.data:
        row = res.data[0]
        return str(row["id"]), _row_to_customer(row)
    # Suche nach Username
    res = _db().table("customers").select("*").eq("username", username_or_email).execute()
    if res.data:
        row = res.data[0]
        return str(row["id"]), _row_to_customer(row)
    return None, None


def _row_to_customer(row: dict) -> dict:
    return {
        "name": row.get("name", ""),
        "firma": row.get("firma", ""),
        "email": row.get("email", ""),
        "username": row.get("username", ""),
        "telefon": row.get("telefon", ""),
        "adresse": row.get("adresse", ""),
        "credits": int(row.get("credits", 0)),
        "erstellt_am": row.get("erstellt_am", ""),
    }


def get_credits(username_or_email: str) -> int:
    _, data = find_customer(username_or_email)
    if data:
        return int(data.get("credits", 0))
    return 0


def deduct_credit(username_or_email: str) -> bool:
    kid, data = find_customer(username_or_email)
    if kid and data and int(data.get("credits", 0)) > 0:
        new_credits = int(data["credits"]) - 1
        _db().table("customers").update({"credits": new_credits}).eq("id", kid).execute()
        return True
    return False


def update_credits(kunde_id: str, credits: int):
    _db().table("customers").update({"credits": int(credits)}).eq("id", kunde_id).execute()


def create_customer(name: str, firma: str, email: str,
                    username: str = "", telefon: str = "",
                    adresse: str = "", credits: int = 0) -> str:
    row = {
        "name": name,
        "firma": firma,
        "email": email,
        "username": username,
        "telefon": telefon,
        "adresse": adresse,
        "credits": credits,
        "erstellt_am": date.today().strftime("%d.%m.%Y"),
    }
    res = _db().table("customers").insert(row).execute()
    if res.data:
        return str(res.data[0]["id"])
    return ""


def update_customer(kunde_id: str, **kwargs):
    _db().table("customers").update(kwargs).eq("id", kunde_id).execute()


def delete_customer(kunde_id: str):
    # Erst Logins entfernen
    res = _db().table("customers").select("email, username").eq("id", kunde_id).execute()
    if res.data:
        row = res.data[0]
        if row.get("email"):
            delete_login(row["email"])
        if row.get("username"):
            delete_login(row["username"])
    _db().table("customers").delete().eq("id", kunde_id).execute()


# ============================================================
# NOTFALLKONTAKTE
# ============================================================
def get_notfall() -> dict:
    res = _db().table("notfall").select("*").execute()
    data = {}
    for row in res.data:
        nid = str(row["id"])
        data[nid] = {
            "name": row.get("name", ""),
            "tel": row.get("tel", ""),
            "desc": row.get("beschreibung", ""),
            "icon": row.get("icon", "📞"),
            "owner": row.get("owner", "all"),
        }
    return data


def save_notfall(data: dict):
    pass  # Nicht nötig bei Supabase – Einzeloperationen


def add_notfall(name: str, tel: str, desc: str, icon: str, owner: str) -> str:
    row = {"name": name, "tel": tel, "beschreibung": desc, "icon": icon, "owner": owner}
    res = _db().table("notfall").insert(row).execute()
    if res.data:
        return str(res.data[0]["id"])
    return ""


def delete_notfall(nid: str):
    _db().table("notfall").delete().eq("id", nid).execute()


# ============================================================
# GEFAHRSTOFFKATASTER
# ============================================================
def get_gefahrstoffe() -> dict:
    res = _db().table("gefahrstoffe").select("*").execute()
    data = {}
    for row in res.data:
        gid = str(row["id"])
        data[gid] = {
            "name": row.get("name", ""),
            "handelsbezeichnung": row.get("handelsbezeichnung", ""),
            "hersteller": row.get("hersteller", ""),
            "kategorie": row.get("kategorie", ""),
            "cas_nummer": row.get("cas_nummer", ""),
            "lagerort": row.get("lagerort", ""),
            "menge": row.get("menge", ""),
            "sdb_datum": row.get("sdb_datum", ""),
            "ghs_symbole": row.get("ghs_symbole", ""),
            "gefahrenbeschreibung": row.get("gefahrenbeschreibung", ""),
            "schutzmassnahmen": row.get("schutzmassnahmen", ""),
            "verwendung": row.get("verwendung", ""),
            "betriebsanweisung_vorhanden": row.get("betriebsanweisung_vorhanden", "Nein"),
            "substitution": row.get("substitution", ""),
            "sdb_link": row.get("sdb_link", ""),
            "owner": row.get("owner", "all"),
            "erstellt_am": row.get("erstellt_am", ""),
        }
    return data


def save_gefahrstoffe(data: dict):
    pass  # Nicht nötig bei Supabase


def add_gefahrstoff(owner: str = "all", **kwargs) -> str:
    row = {**kwargs, "owner": owner, "erstellt_am": date.today().strftime("%d.%m.%Y")}
    # Entferne Keys die nicht in der Tabelle sind
    allowed = {"name", "handelsbezeichnung", "hersteller", "kategorie", "cas_nummer",
               "lagerort", "menge", "sdb_datum", "ghs_symbole", "gefahrenbeschreibung",
               "schutzmassnahmen", "verwendung", "betriebsanweisung_vorhanden",
               "substitution", "sdb_link", "owner", "erstellt_am"}
    row = {k: v for k, v in row.items() if k in allowed}
    res = _db().table("gefahrstoffe").insert(row).execute()
    if res.data:
        return str(res.data[0]["id"])
    return ""


def delete_gefahrstoff(gid: str):
    _db().table("gefahrstoffe").delete().eq("id", gid).execute()


# ============================================================
# BERICHTE (Audit-Trail) – NEU!
# ============================================================
def save_bericht(projekt: str, inspektor: str, status: str,
                 anzahl_maengel: int, erstellt_von: str, ergebnisse: list = None):
    """Speichert einen Bericht für den Audit-Trail."""
    import json
    row = {
        "projekt": projekt,
        "inspektor": inspektor,
        "status": status,
        "anzahl_maengel": anzahl_maengel,
        "erstellt_von": erstellt_von,
        "ergebnisse": json.dumps(ergebnisse or [], ensure_ascii=False),
    }
    _db().table("berichte").insert(row).execute()


def get_berichte(erstellt_von: str = None) -> list:
    """Gibt Berichte zurück (optional gefiltert nach Ersteller)."""
    query = _db().table("berichte").select("*").order("created_at", desc=True)
    if erstellt_von:
        query = query.eq("erstellt_von", erstellt_von)
    res = query.execute()
    return res.data if res.data else []


# ============================================================
# MIGRATION (Kompatibilität mit altem Code)
# ============================================================
def migrate_legacy_data():
    """
    Migration von alten JSON-Dateien zu Supabase.
    Prüft ob Admin existiert und hasht Klartext-Passwörter.
    """
    # Sicherstellen dass Admin existiert
    res = _db().table("users").select("id, password_hash").eq("username", "admin").execute()
    if res.data:
        stored = res.data[0]["password_hash"]
        # Wenn noch Klartext oder temp-Passwort
        if needs_rehash(stored) or stored == "temp_1234":
            hashed = hash_password("1234")
            _db().table("users").update({"password_hash": hashed}).eq("username", "admin").execute()
    else:
        hashed = hash_password("1234")
        _db().table("users").insert({"username": "admin", "password_hash": hashed}).execute()


def new_id() -> str:
    """Nicht mehr nötig – Supabase generiert UUIDs automatisch."""
    import uuid
    return str(uuid.uuid4())[:8]
