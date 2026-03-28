"""
SafeSite Drohne – KI-Analyse-Engine
Gemini API Integration für Sicherheitsanalyse.
"""
import json
import time
import cv2
import streamlit as st
from google import genai

from config import GEMINI_MODELS, get_api_key


def clean_json(text: str) -> str:
    """Extrahiert JSON-Array aus API-Antwort."""
    text = text.strip()
    first = text.find("[")
    last = text.rfind("]")
    if first != -1 and last != -1:
        return text[first : last + 1]
    return text


def get_video_duration(video_path: str) -> float:
    """Gibt die Videolänge in Sekunden zurück."""
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


def build_prompt(num_files: int, video_duration: float = 30.0) -> str:
    """Erstellt den Analyse-Prompt mit BauAV-Referenzen."""
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


def run_analysis(m_type: str, m_files: list) -> list:
    """
    Führt die KI-Analyse durch.
    Probiert Gemini-Modelle der Reihe nach durch.
    Gibt eine Liste von Mängeln zurück.
    """
    api_key = get_api_key()
    client = genai.Client(api_key=api_key, http_options={"timeout": 120000})

    # Video-Dauer ermitteln
    video_duration = 30.0
    if m_type == "video":
        video_duration = get_video_duration(m_files[0])

    prompt = build_prompt(len(m_files), video_duration)
    status = st.empty()
    start = time.time()

    last_error = None

    for model_name in GEMINI_MODELS:
        try:
            elapsed = int(time.time() - start)

            if m_type == "video":
                status.info(f"🔄 Lade Video hoch... ({elapsed}s)")
                uploaded = client.files.upload(file=m_files[0])
                while uploaded.state.name == "PROCESSING":
                    elapsed = int(time.time() - start)
                    status.info(f"🔄 Video wird verarbeitet... ({elapsed}s)")
                    time.sleep(2)
                    uploaded = client.files.get(name=uploaded.name)

                status.info(f"🔄 Analysiere nach BauAV & SUVA... ({elapsed}s)")
                res = client.models.generate_content(
                    model=model_name,
                    contents=[uploaded, prompt],
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
            else:
                # Bilder hochladen
                uploaded_files = []
                for idx, path in enumerate(m_files):
                    elapsed = int(time.time() - start)
                    status.info(f"🔄 Lade Bild {idx+1}/{len(m_files)}... ({elapsed}s)")
                    try:
                        f = client.files.upload(file=path)
                        uploaded_files.append(f)
                    except Exception as e:
                        st.warning(f"⚠️ Bild {idx+1} übersprungen: {e}")

                if not uploaded_files:
                    status.error("❌ Keine Bilder konnten hochgeladen werden.")
                    continue

                # Warten bis verarbeitet
                for idx, f in enumerate(uploaded_files):
                    while f.state.name == "PROCESSING":
                        elapsed = int(time.time() - start)
                        status.info(f"🔄 Verarbeite Bild {idx+1}... ({elapsed}s)")
                        time.sleep(2)
                        f = client.files.get(name=f.name)
                        uploaded_files[idx] = f

                elapsed = int(time.time() - start)
                status.info(f"🔄 Analysiere nach BauAV & SUVA... ({elapsed}s)")
                res = client.models.generate_content(
                    model=model_name,
                    contents=[prompt] + uploaded_files,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

            # Erfolgreich!
            elapsed = int(time.time() - start)
            status.success(f"✅ Analyse abgeschlossen ({elapsed}s)")
            time.sleep(0.5)
            status.empty()

            result = json.loads(clean_json(res.text))
            if isinstance(result, list):
                return result
            return []

        except Exception as e:
            last_error = str(e)
            elapsed = int(time.time() - start)
            status.warning(f"⚠️ Modell {model_name} fehlgeschlagen, versuche nächstes... ({elapsed}s)")
            continue

    status.error(f"❌ Alle Modelle fehlgeschlagen. Letzter Fehler: {last_error}")
    return []
