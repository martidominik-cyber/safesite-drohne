"""
SafeSite Drohne – KI-Analyse-Engine (Dual-AI-Verification)

Ablauf:
  1. Gemini analysiert Bilder/Video → findet Mängel
  2. Claude Opus prüft die gleichen Bilder + Gemini-Ergebnisse
     → bestätigt, korrigiert, ergänzt fehlende Mängel
  3. Zusammenführung: Mängel aus beiden KIs → Vertrauenslevel
     ✅✅ = Beide KIs einig → Hohe Sicherheit
     ⚠️  = Nur eine KI → Manuelle Prüfung empfohlen
"""
import json
import time
import base64
import os
import cv2
import streamlit as st
from google import genai

from config import GEMINI_MODELS, CLAUDE_MODEL, get_api_key, get_anthropic_key


# ============================================================
# HILFSFUNKTIONEN
# ============================================================
def clean_json(text: str) -> str:
    """Extrahiert JSON-Array aus API-Antwort."""
    text = text.strip()
    first = text.find("[")
    last = text.rfind("]")
    if first != -1 and last != -1:
        return text[first : last + 1]
    return text


def get_video_duration(video_path: str) -> float:
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        if fps > 0:
            return frames / fps
    except Exception:
        pass
    return 30.0


def image_to_base64(path: str) -> tuple:
    """Liest ein Bild und gibt (base64_string, media_type) zurück."""
    ext = os.path.splitext(path)[1].lower()
    media_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
        ".gif": "image/gif",
    }
    media_type = media_map.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def extract_video_frames(video_path: str, num_frames: int = 6) -> list:
    """Extrahiert gleichmässig verteilte Frames aus einem Video als temp JPEGs."""
    duration = get_video_duration(video_path)
    timestamps = [duration * i / (num_frames + 1) for i in range(1, num_frames + 1)]
    frames = []
    try:
        cap = cv2.VideoCapture(video_path)
        for ts in timestamps:
            cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
            ret, frame = cap.read()
            if ret:
                path = f"temp_frame_{len(frames)}.jpg"
                cv2.imwrite(path, frame)
                frames.append(path)
        cap.release()
    except Exception:
        pass
    return frames


# ============================================================
# GEMINI PROMPT
# ============================================================
def build_gemini_prompt(num_files: int, video_duration: float = 30.0) -> str:
    max_ts = max(0, video_duration - 1)
    return f"""
Du bist ein äusserst strenger und erfahrener Schweizer Bau-Sicherheitsprüfer (SiBe) mit tiefem Wissen der BauAV und SUVA-Richtlinien.

KRITISCH: Du erhältst {num_files} Bilder zur Analyse. Analysiere JEDES Bild MILLIMETERGENAU und SYSTEMATISCH nach ALLEN relevanten Schweizer Sicherheitsnormen (BauAV und SUVA).

KRITISCH: Der Parameter "bild_index" muss der Index des Bildes sein (0 für das erste Bild, 1 für das zweite, etc.).

PRÜFUNGSPROTOKOLL – Prüfe ALLE folgenden Punkte für JEDES Bild:

1. GERÜSTE (BauAV Art. 47–65): Abstand Fassade <30cm, dreiteiliger Seitenschutz (Holm/Zwischenholm/Bordbrett), Höhe ≥100cm, Bordbrett ≥15cm, Belagsbreite ≥60cm, Fundation, Verankerung, Nutzlastschild, Rollgerüste Räder arretiert.

2. ABSTURZKANTEN (BauAV Art. 22–26): Seitenschutz ab 2m, Fassadengerüst ab 3m bei Hochbau, Bodenöffnungen gesichert, Niveauunterschiede >50cm.

3. DÄCHER (BauAV Art. 41–46): Ab 2m Massnahmen an Dachrändern, Neigungsabhängige Sicherung, nicht durchbruchsichere Flächen, Dachöffnungen.

4. LEITERN (BauAV Art. 20–21): Zustand, gegen Wegrutschen gesichert, oberste Sprossen, Arbeiten >2m.

5. PSA (BauAV Art. 6–7): Schutzhelm bei Hochbau/Rohbau/Kran/Gerüstbau, Warnkleider bei Baumaschinen.

6. VERKEHRSWEGE (BauAV Art. 11, 15): Breite ≥1m/60cm, frei, Gleitgefahr, Steigung, Handlauf ab 5 Stufen.

7. HERABFALLENDE GEGENSTÄNDE (BauAV Art. 17–18): Absperrung, Schutzeinrichtungen.

8. BAUMASCHINEN (BauAV Art. 19): Gefahrenbereich, Kameras/Spiegel.

9. ELEKTRIZITÄT (BauAV Art. 30–31): FI-Schutzschalter, Kabelzustand.

10. BRANDSCHUTZ (BauAV Art. 34): Löschmittel, Fluchtwege.

11. GRÄBEN (BauAV Art. 68–78): Ab 1.5m Spriessung/Böschung, Grabenrand freihalten, Zugänge.

12. GESUNDHEIT (BauAV Art. 36–38): Gehörschutz, Hitze/Kälte, Beleuchtung.

REGELN:
- Priorität: "Kritisch" = Lebensgefahr, "Hoch" = Schwere Verstösse, "Mittel" = Normative Abweichungen
- Referenziere IMMER genaue BauAV-Artikel (z.B. "BauAV Art. 6 Abs. 2")
- Wenn du etwas NICHT SICHER ERKENNEN kannst = Mangel melden!
- VIDEOS: Das Video ist {video_duration:.0f}s lang. zeitstempel_sekunden MUSS zwischen 0 und {max_ts:.0f} liegen!
- Jeder Mangel braucht einen ANDEREN Zeitstempel/bild_index!
- Schreibe DETAILLIERTE, PROFESSIONELLE Texte!

Antworte NUR als JSON:
[{{"kategorie": "...", "prioritaet": "Kritisch/Hoch/Mittel", "mangel": "DETAILLIERTE BESCHREIBUNG...", "verstoss": "Verstoss BauAV Art. X...", "massnahme": "KONKRETE Massnahme...", "zeitstempel_sekunden": 0, "bild_index": 0}}]
"""


# ============================================================
# CLAUDE REVIEW PROMPT
# ============================================================
def build_claude_prompt(gemini_findings: list, num_images: int) -> str:
    findings_json = json.dumps(gemini_findings, ensure_ascii=False, indent=2)
    return f"""Du bist ein äusserst strenger und erfahrener Schweizer Bau-Sicherheitsprüfer (SiBe) und Qualitätskontrolleur. Deine Aufgabe ist eine ZWEITE, UNABHÄNGIGE Prüfung.

Eine erste KI (Gemini) hat die Baustellen-Bilder bereits analysiert. Hier sind deren Ergebnisse:

<gemini_ergebnisse>
{findings_json}
</gemini_ergebnisse>

Du erhältst die gleichen {num_images} Bilder. Deine Aufgabe:

1. EIGENE ANALYSE: Analysiere JEDES Bild selbst nach BauAV und SUVA-Richtlinien.

2. PRÜFE Gemini's Ergebnisse kritisch:
   - Sind die Mängel KORREKT erkannt? (Nicht übertrieben, nicht untertrieben?)
   - Stimmen die BauAV-Artikel-Referenzen?
   - Sind die Prioritäten richtig gesetzt?

3. ERGÄNZE fehlende Mängel die Gemini ÜBERSEHEN hat.

4. KORRIGIERE falsche Angaben (z.B. falsche Artikel-Nummern, falsche Priorität).

5. ENTFERNE unbegründete Mängel (z.B. wenn Gemini etwas sieht, das gar nicht existiert).

Antworte NUR als JSON mit diesem Format:
[{{
  "kategorie": "...",
  "prioritaet": "Kritisch/Hoch/Mittel",
  "mangel": "DETAILLIERTE BESCHREIBUNG...",
  "verstoss": "Verstoss BauAV Art. X...",
  "massnahme": "KONKRETE Massnahme...",
  "zeitstempel_sekunden": 0,
  "bild_index": 0,
  "verifikation": "bestaetigt/korrigiert/neu/entfernt",
  "verifikation_detail": "Kurze Begründung was geändert/ergänzt wurde"
}}]

REGELN:
- "verifikation": "bestaetigt" = Gemini hatte Recht, Mangel bestätigt
- "verifikation": "korrigiert" = Gemini hatte den Mangel, aber Details waren falsch (z.B. falscher Artikel)
- "verifikation": "neu" = Mangel den Gemini ÜBERSEHEN hat
- "verifikation": "entfernt" = Gemini hat etwas gemeldet das KEIN echter Mangel ist (dann Begründung warum)
- bild_index: 0 für erstes Bild, 1 für zweites, etc.
- Referenziere IMMER die korrekten BauAV-Artikel!
"""


# ============================================================
# SCHRITT 1: GEMINI ANALYSE
# ============================================================
def run_gemini(m_type: str, m_files: list, status_placeholder) -> list:
    """Führt die Gemini-Analyse durch."""
    api_key = get_api_key()
    client = genai.Client(api_key=api_key, http_options={"timeout": 120000})

    video_duration = 30.0
    if m_type == "video":
        video_duration = get_video_duration(m_files[0])

    prompt = build_gemini_prompt(len(m_files), video_duration)
    start = time.time()
    last_error = None

    for model_name in GEMINI_MODELS:
        try:
            elapsed = int(time.time() - start)

            if m_type == "video":
                status_placeholder.info(f"🔄 **Gemini** lädt Video hoch... ({elapsed}s)")
                uploaded = client.files.upload(file=m_files[0])
                while uploaded.state.name == "PROCESSING":
                    elapsed = int(time.time() - start)
                    status_placeholder.info(f"🔄 **Gemini** verarbeitet Video... ({elapsed}s)")
                    time.sleep(2)
                    uploaded = client.files.get(name=uploaded.name)

                status_placeholder.info(f"🔄 **Gemini** analysiert nach BauAV & SUVA... ({elapsed}s)")
                res = client.models.generate_content(
                    model=model_name,
                    contents=[uploaded, prompt],
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            else:
                uploaded_files = []
                for idx, path in enumerate(m_files):
                    elapsed = int(time.time() - start)
                    status_placeholder.info(f"🔄 **Gemini** lädt Bild {idx+1}/{len(m_files)}... ({elapsed}s)")
                    try:
                        f = client.files.upload(file=path)
                        uploaded_files.append(f)
                    except Exception as e:
                        st.warning(f"⚠️ Bild {idx+1} übersprungen: {e}")

                if not uploaded_files:
                    continue

                for idx, f in enumerate(uploaded_files):
                    while f.state.name == "PROCESSING":
                        elapsed = int(time.time() - start)
                        status_placeholder.info(f"🔄 **Gemini** verarbeitet Bild {idx+1}... ({elapsed}s)")
                        time.sleep(2)
                        f = client.files.get(name=f.name)
                        uploaded_files[idx] = f

                elapsed = int(time.time() - start)
                status_placeholder.info(f"🔄 **Gemini** analysiert nach BauAV & SUVA... ({elapsed}s)")
                res = client.models.generate_content(
                    model=model_name,
                    contents=[prompt] + uploaded_files,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

            elapsed = int(time.time() - start)
            status_placeholder.success(f"✅ **Gemini** Analyse abgeschlossen ({elapsed}s)")

            result = json.loads(clean_json(res.text))
            return result if isinstance(result, list) else []

        except Exception as e:
            last_error = str(e)
            status_placeholder.warning(f"⚠️ Gemini {model_name} fehlgeschlagen, versuche nächstes...")
            continue

    status_placeholder.error(f"❌ Gemini fehlgeschlagen: {last_error}")
    return []


# ============================================================
# SCHRITT 2: CLAUDE VERIFICATION
# ============================================================
def run_claude_review(m_type: str, m_files: list, gemini_findings: list,
                      status_placeholder) -> list:
    """Claude Opus prüft die Bilder + Gemini-Ergebnisse."""
    anthropic_key = get_anthropic_key()
    if not anthropic_key:
        status_placeholder.warning("⚠️ Kein Anthropic API Key – Claude-Verification übersprungen.")
        return []

    try:
        import anthropic
    except ImportError:
        status_placeholder.warning("⚠️ anthropic-Paket fehlt – Claude-Verification übersprungen.")
        return []

    client = anthropic.Anthropic(api_key=anthropic_key)
    start = time.time()

    # Bilder für Claude vorbereiten
    image_content = []
    temp_frames = []

    if m_type == "video":
        # Video-Frames extrahieren für Claude
        status_placeholder.info("🔄 **Claude Opus** extrahiert Video-Frames...")
        temp_frames = extract_video_frames(m_files[0], num_frames=6)
        image_paths = temp_frames
    else:
        image_paths = m_files

    # Bilder als base64 für Claude
    for idx, path in enumerate(image_paths):
        try:
            elapsed = int(time.time() - start)
            status_placeholder.info(f"🔄 **Claude Opus** bereitet Bild {idx+1}/{len(image_paths)} vor... ({elapsed}s)")
            b64_data, media_type = image_to_base64(path)
            image_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": b64_data,
                },
            })
        except Exception as e:
            st.warning(f"⚠️ Bild {idx+1} für Claude übersprungen: {e}")

    if not image_content:
        status_placeholder.warning("⚠️ Keine Bilder für Claude verfügbar.")
        # Temp-Frames aufräumen
        for f in temp_frames:
            try: os.remove(f)
            except: pass
        return []

    # Claude-Prompt
    prompt_text = build_claude_prompt(gemini_findings, len(image_paths))

    # API-Aufruf
    elapsed = int(time.time() - start)
    status_placeholder.info(f"🔄 **Claude Opus** prüft Gemini-Ergebnisse... ({elapsed}s)")

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": image_content + [{"type": "text", "text": prompt_text}],
            }],
        )

        # Antwort verarbeiten
        response_text = ""
        for block in message.content:
            if hasattr(block, "text"):
                response_text += block.text

        elapsed = int(time.time() - start)
        status_placeholder.success(f"✅ **Claude Opus** Verification abgeschlossen ({elapsed}s)")

        result = json.loads(clean_json(response_text))

        # Temp-Frames aufräumen
        for f in temp_frames:
            try: os.remove(f)
            except: pass

        return result if isinstance(result, list) else []

    except Exception as e:
        elapsed = int(time.time() - start)
        status_placeholder.error(f"❌ Claude Fehler ({elapsed}s): {e}")
        # Temp-Frames aufräumen
        for f in temp_frames:
            try: os.remove(f)
            except: pass
        return []


# ============================================================
# SCHRITT 3: ZUSAMMENFÜHRUNG
# ============================================================
def merge_findings(gemini: list, claude: list) -> list:
    """
    Führt Gemini- und Claude-Ergebnisse zusammen.
    Vertrauenslevel:
      ✅✅ BESTÄTIGT = Beide KIs einig
      🔄 KORRIGIERT = Claude hat Gemini's Mangel korrigiert
      🆕 NEU        = Nur Claude hat diesen Mangel gefunden
      ❌ ENTFERNT   = Claude sagt: kein echter Mangel
      ⚠️ NUR GEMINI = Nur Gemini hat diesen Mangel (Claude hat nicht reagiert)
    """
    if not claude:
        # Fallback: Nur Gemini-Ergebnisse (kein Claude verfügbar)
        for item in gemini:
            item["verifikation"] = "nur_gemini"
            item["verifikation_label"] = "⚠️ Nur Gemini"
        return gemini

    merged = []
    gemini_matched = set()

    for c_item in claude:
        verif = c_item.get("verifikation", "bestaetigt")

        if verif == "entfernt":
            # Claude sagt: kein Mangel → nicht aufnehmen, aber loggen
            continue

        if verif == "bestaetigt":
            c_item["verifikation_label"] = "✅✅ Bestätigt (Dual-AI)"
        elif verif == "korrigiert":
            c_item["verifikation_label"] = "🔄 Korrigiert durch Claude"
        elif verif == "neu":
            c_item["verifikation_label"] = "🆕 Zusätzlich gefunden (Claude)"
        else:
            c_item["verifikation_label"] = "✅✅ Bestätigt (Dual-AI)"

        # Finde den passenden Gemini-Eintrag (nach bild_index + ähnlicher Kategorie)
        for g_idx, g_item in enumerate(gemini):
            if g_idx in gemini_matched:
                continue
            if (g_item.get("bild_index") == c_item.get("bild_index") and
                g_item.get("kategorie", "").lower() == c_item.get("kategorie", "").lower()):
                gemini_matched.add(g_idx)
                break

        merged.append(c_item)

    # Gemini-Mängel die Claude nicht erwähnt hat
    for g_idx, g_item in enumerate(gemini):
        if g_idx not in gemini_matched:
            g_item["verifikation"] = "nur_gemini"
            g_item["verifikation_label"] = "⚠️ Nur Gemini"
            merged.append(g_item)

    # Sortieren: Kritisch → Hoch → Mittel
    prio_order = {"Kritisch": 0, "Hoch": 1, "Mittel": 2}
    merged.sort(key=lambda x: prio_order.get(x.get("prioritaet", "Mittel"), 3))

    return merged


# ============================================================
# HAUPTFUNKTION: DUAL-AI ANALYSE
# ============================================================
def run_analysis(m_type: str, m_files: list) -> list:
    """
    Führt die komplette Dual-AI-Analyse durch:
    1. Gemini analysiert
    2. Claude Opus verifiziert
    3. Ergebnisse zusammenführen
    """
    st.markdown("### 🔬 Dual-AI-Verification")

    # Fortschritts-Container
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🟡 KI 1: Google Gemini**")
        gemini_status = st.empty()
    with col2:
        st.markdown("**🟣 KI 2: Claude Opus**")
        claude_status = st.empty()

    progress = st.progress(0, text="Starte Dual-AI-Analyse...")

    # SCHRITT 1: Gemini
    progress.progress(10, text="Schritt 1/3: Gemini analysiert...")
    gemini_findings = run_gemini(m_type, m_files, gemini_status)

    if not gemini_findings:
        progress.progress(100, text="❌ Gemini konnte keine Mängel finden.")
        return []

    gemini_status.success(f"✅ **Gemini**: {len(gemini_findings)} Mängel gefunden")

    # SCHRITT 2: Claude Review
    progress.progress(50, text="Schritt 2/3: Claude Opus verifiziert...")
    claude_status.info("🔄 **Claude Opus** startet Verification...")
    claude_findings = run_claude_review(m_type, m_files, gemini_findings, claude_status)

    if claude_findings:
        confirmed = sum(1 for f in claude_findings if f.get("verifikation") == "bestaetigt")
        new_found = sum(1 for f in claude_findings if f.get("verifikation") == "neu")
        corrected = sum(1 for f in claude_findings if f.get("verifikation") == "korrigiert")
        claude_status.success(
            f"✅ **Claude Opus**: {confirmed} bestätigt, "
            f"{new_found} neu, {corrected} korrigiert"
        )
    else:
        claude_status.warning("⚠️ Claude-Verification nicht verfügbar")

    # SCHRITT 3: Zusammenführen
    progress.progress(90, text="Schritt 3/3: Ergebnisse zusammenführen...")
    merged = merge_findings(gemini_findings, claude_findings)

    progress.progress(100, text="✅ Dual-AI-Verification abgeschlossen!")
    time.sleep(0.5)
    progress.empty()

    return merged
