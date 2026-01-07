import streamlit as st
import google.generativeai as genai
import cv2
import tempfile
import os
import json
from fpdf import FPDF
import time
from datetime import date
from PIL import Image
# Falls python-docx fehlt, fangen wir den Fehler ab, damit die App nicht crasht
try:
    from docx import Document
    from docx.shared import Inches
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False

# ==========================================
# 0. KONFIGURATION
# ==========================================
st.set_page_config(page_title="SafeSite Drohne", page_icon="logo.jpg", layout="wide", initial_sidebar_state="auto")

# ----------------------------------------------------
# 🔴 HIER DEINEN GITHUB-NAMEN EINTRAGEN!
LOGO_URL_GITHUB = "https://raw.githubusercontent.com/DEIN_BENUTZERNAME/safesite-drohne/main/logo.jpg?v=1"
# ----------------------------------------------------

# STYLE
st.markdown(f"""
<style>
    .stAppDeployButton {{display: none;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebarCollapsedControl"] {{color: #FF6600 !important;}}
</style>
<link rel="apple-touch-icon" href="{LOGO_URL_GITHUB}">
""", unsafe_allow_html=True)

# DATENBANK
USER_DB_FILE = "users.json"
def load_users():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f: json.dump({"admin": "1234"}, f)
    with open(USER_DB_FILE, "r") as f: return json.load(f)

# API KEY CHECK
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key fehlt in den Secrets!")
    st.stop()

# ==========================================
# 1. FUNKTIONEN
# ==========================================
def clean_json(text):
    text = text.strip()
    first_bracket = text.find('[')
    last_bracket = text.rfind(']')
    if first_bracket != -1 and last_bracket != -1:
        text = text[first_bracket:last_bracket+1]
    return text

def extract_frame(video_path, timestamp):
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read(); cap.release()
        if ret: return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except: return None

def convert_image_to_supported_format(image_path):
    """
    Konvertiert Bilder (insbesondere MPO) in ein von Gemini unterstütztes Format (JPEG/PNG).
    """
    try:
        img = Image.open(image_path)
        img_format = img.format or ''
        
        # Wenn das Bild MPO ist oder ein nicht unterstütztes Format, konvertiere es
        if img_format.upper() == 'MPO' or (img_format and img_format.upper() not in ['JPEG', 'PNG', 'WEBP', 'JPG']):
            # Konvertiere zu RGB (falls notwendig)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Speichere als temporäre JPEG-Datei
            temp_path = image_path.replace('.mpo', '.jpg').replace('.MPO', '.jpg')
            if temp_path == image_path:  # Falls kein .mpo gefunden wurde
                base_name = image_path.rsplit('.', 1)[0] if '.' in image_path else image_path
                temp_path = base_name + '_converted.jpg'
            
            img.save(temp_path, 'JPEG', quality=95)
            return temp_path
        
        # Wenn bereits unterstütztes Format, prüfe ob RGB-Modus
        if img.mode != 'RGB':
            img = img.convert('RGB')
            base_name = image_path.rsplit('.', 1)[0] if '.' in image_path else image_path
            temp_path = base_name + '_converted.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            return temp_path
        
        return image_path
    except Exception as e:
        # Falls Konvertierung fehlschlägt, gib Original zurück
        return image_path

# --- PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        # Logo oben RECHTS platzieren (x=160, y=8)
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 160, 8, 40)
            except: pass
        
        # Kleiner Header auf jeder Seite (ausser der ersten, das machen wir manuell)
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, 'SafeSite Drohne - Sicherheitsbericht', ln=True, align='R')
        self.ln(5)

def create_pdf(data, m_type, m_files, projekt_name, inspektor_name, status_text):
    pdf = PDF()
    pdf.add_page()
    
    # --- TITELBEREICH (Wie Screenshot 1) ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SICHERHEITS-INSPEKTION (DROHNE)", ln=True)
    pdf.ln(10)
    
    # Metadaten Tabelle
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(30, 8, "Projekt:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(70, 8, projekt_name, ln=0)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(20, 8, "Datum:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, date.today().strftime('%d. %B %Y'), ln=True) # z.B. 08. Januar 2026
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(30, 8, "Inspektor:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(70, 8, f"{inspektor_name} (SafeSite Drohne)", ln=0)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(20, 8, "Status:", ln=0)
    pdf.set_font("Arial", '', 11)
    # Status mit Farbe simulieren (Text)
    pdf.set_text_color(255, 153, 51) if "Massnahmen" in status_text else pdf.set_text_color(0, 153, 0)
    pdf.cell(0, 8, status_text, ln=True)
    pdf.set_text_color(0, 0, 0) # Reset Farbe
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. ZUSAMMENFASSUNG / MÄNGELLISTE", ln=True)
    pdf.ln(5)
    
    # --- MÄNGELLISTE ---
    for i, item in enumerate(data):
        if pdf.get_y() > 220: pdf.add_page()
        
        # Titel Rot und Fett
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(204, 0, 0)
        titel = f"{i+1}. {item.get('kategorie', 'Mangel')} ({item.get('prioritaet', 'Mittel')})"
        pdf.cell(0, 8, titel.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Text Schwarz
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
        
        # Inhalt
        pdf.multi_cell(0, 5, f"Mangel: {item.get('mangel', '-').encode('latin-1', 'replace').decode('latin-1')}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Verstoss: {item.get('verstoss', '-').encode('latin-1', 'replace').decode('latin-1')}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Massnahme: {item.get('massnahme', '-').encode('latin-1', 'replace').decode('latin-1')}")
        pdf.ln(5)
        
        # Bild
        img_path = None
        temp_created = False
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_{i}.jpg"
                cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                temp_created = True
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
            
        if img_path:
            try: pdf.image(img_path, x=20, w=120)
            except: pass
            pdf.ln(10)
            if temp_created and os.path.exists(img_path): os.remove(img_path)
    
    # --- SCHLUSSSEITE (Unterschriften) ---
    if pdf.get_y() > 200: pdf.add_page()
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. FREIGABE", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Dieser Bericht wurde generiert durch SafeSite Drohne.", ln=True)
    
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Hinweis: Dieser Bericht dient als visuelle Unterstützung. Er entbindet die zuständige Bauleitung nicht von der gesetzlichen Kontrollpflicht. Keine Garantie auf Vollständigkeit.")
    pdf.ln(20)
    
    # Unterschriftenblock
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 10, "Erstellt durch:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(80, 10, f"{inspektor_name} (SafeSite)", ln=0) # Name aus Input
    pdf.cell(0, 10, "__________________________ (Datum / Unterschrift)", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 10, "Verantwortlicher Polier:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(80, 10, "__________________________", ln=0)
    pdf.cell(0, 10, "__________________________ (Datum / Unterschrift)", ln=True)

    out = "Bericht.pdf"
    pdf.output(out)
    return out    

# --- WORD GENERATOR ---
def create_word(data, m_type, m_files, projekt_name, inspektor_name, status_text):
    if not WORD_AVAILABLE: return None
    doc = Document()
    
    # Logo (Versuch rechtsbündig, falls python-docx das Bild findet)
    if os.path.exists(LOGO_FILE):
        try:
            doc.add_picture(LOGO_FILE, width=Inches(1.5))
            last_paragraph = doc.paragraphs[-1] 
            last_paragraph.alignment = 2 # 2 = Rechtsbündig
        except: pass

    # Header Daten
    h = doc.add_heading('SICHERHEITS-INSPEKTION (DROHNE)', 0)
    
    p = doc.add_paragraph()
    p.add_run("Projekt: ").bold = True; p.add_run(f"{projekt_name}\n")
    p.add_run("Datum: ").bold = True; p.add_run(f"{date.today().strftime('%d. %B %Y')}\n")
    p.add_run("Inspektor: ").bold = True; p.add_run(f"{inspektor_name}\n")
    p.add_run("Status: ").bold = True; p.add_run(f"{status_text} ⚠️")

    doc.add_heading('1. ZUSAMMENFASSUNG / MÄNGEL', level=1)
    
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('kategorie', 'Mangel')}", level=2)
        
        p = doc.add_paragraph()
        p.add_run("Mangel: ").bold = True; p.add_run(f"{item.get('mangel')}\n")
        p.add_run("Verstoss: ").bold = True; p.add_run(f"{item.get('verstoss')}\n")
        p.add_run("Massnahme: ").bold = True; p.add_run(f"{item.get('massnahme')}")
        
        # Bild einfügen
        img_path = None
        temp_created = False
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_word_{i}.jpg"
                cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                temp_created = True
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
            
        if img_path:
            try: doc.add_picture(img_path, width=Inches(4.5))
            except: pass
            if temp_created and os.path.exists(img_path): os.remove(img_path)

    # Footer / Freigabe
    doc.add_page_break()
    doc.add_heading('4. FREIGABE', level=1)
    doc.add_paragraph("Dieser Bericht wurde generiert durch SafeSite Drohne.")
    p = doc.add_paragraph("Hinweis: Dieser Bericht dient als visuelle Unterstützung. Er entbindet die zuständige Bauleitung nicht von der gesetzlichen Kontrollpflicht.")
    p.italic = True
    
    doc.add_paragraph(f"\nErstellt durch: {inspektor_name} (SafeSite) \t____________________ (Datum/Unterschrift)")
    doc.add_paragraph(f"\nVerantwortlicher Polier: \t\t\t____________________ (Datum/Unterschrift)")

    out = "Bericht.docx"
    doc.save(out)
    return out
# ==========================================
# 2. APP OBERFLÄCHE
# ==========================================
if 'app_step' not in st.session_state: st.session_state.app_step = 'screen_a'
if 'analysis_data' not in st.session_state: st.session_state.analysis_data = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'

# SIDEBAR - NAVIGATION
with st.sidebar:
    st.title("SafeSite Drohne")
    
    # Navigation
    page_options = ["🏠 Startseite", "🔍 SafeSite-Check", "📋 SUVA Regeln", "⚖️ BauAV"]
    
    # Index basierend auf current_page bestimmen
    page_index_map = {
        'home': 0,
        'safesite': 1,
        'suva': 2,
        'bauav': 3
    }
    current_index = page_index_map.get(st.session_state.current_page, 0)
    
    page = st.radio(
        "Bereich wählen:",
        page_options,
        index=current_index,
        key="nav"
    )
    
    if page == "🏠 Startseite":
        st.session_state.current_page = 'home'
    elif page == "🔍 SafeSite-Check":
        st.session_state.current_page = 'safesite'
    elif page == "📋 SUVA Regeln":
        st.session_state.current_page = 'suva'
    elif page == "⚖️ BauAV":
        st.session_state.current_page = 'bauav'
    
    # Logout nur anzeigen, wenn im SafeSite-Check eingeloggt
    if st.session_state.current_page == 'safesite' and st.session_state.logged_in:
        st.divider()
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()

# HAUPTBEREICH
if st.session_state.current_page == 'home':
    # STARTSEITE - Kein Login erforderlich
    st.header("🏠 Willkommen bei SafeSite Drohne")
    st.write("Wählen Sie einen Bereich aus der Sidebar aus.")
    st.info("💡 Der SafeSite-Check Bereich erfordert eine Anmeldung.")

elif st.session_state.current_page == 'safesite':
    # SAFESITE-CHECK - Login erforderlich
    if not st.session_state.logged_in:
        st.header("🔍 SafeSite-Check - Login erforderlich")
        u = st.text_input("User")
        p = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.rerun()
            else: 
                st.error("❌ Falscher Benutzername oder Passwort")
    else:
        # HAUPT APP - SafeSite-Check
        if st.session_state.app_step == 'screen_a':
            st.subheader("Neuer Auftrag (Pro-Modell)")
            if not WORD_AVAILABLE:
                st.warning("⚠️ Word-Export nicht verfügbar. Bitte 'python-docx' in requirements.txt ergänzen!")
            
            mode = st.radio("Quelle:", ["📹 Video", "📸 Fotos"], horizontal=True)
            files = []
            
            if mode == "📹 Video":
                vf = st.file_uploader("Video (mp4)", type=["mp4"])
                if vf and st.button("Analyse starten"):
                    t = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); t.write(vf.read()); files.append(t.name); t.close()
                    st.session_state.m_type = "video"; st.session_state.m_files = files; st.session_state.app_step = 'screen_b'; st.rerun()
            else:
                pf = st.file_uploader("Fotos (jpg, png)", type=["jpg", "png"], accept_multiple_files=True)
                if pf and st.button("Analyse starten"):
                    for f in pf:
                        t = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg'); t.write(f.read()); files.append(t.name); t.close()
                    st.session_state.m_type = "images"; st.session_state.m_files = files; st.session_state.app_step = 'screen_b'; st.rerun()

        elif st.session_state.app_step == 'screen_b':
            st.subheader("🕵️‍♂️ Gemini 3.0 Pro analysiert...")
            
            if st.session_state.m_type == "video": st.video(st.session_state.m_files[0])
            else: 
                # --- HIER WAR DER FEHLER (jetzt korrigiert) ---
                cols = st.columns(3)
                for i, f in enumerate(st.session_state.m_files):
                    with cols[i % 3]:
                        st.image(f, caption=f"Bild {i+1}")
                # ----------------------------------------------

            if not st.session_state.analysis_data:
                with st.spinner("Ich denke nach... (Gemini 3.0 Pro analysiert...)"):
                    try:
                        genai.configure(api_key=API_KEY)
                        
                        # PROMPT (Optimiert auf Basis deines Feedbacks)
                        prompt = """
                        Du bist ein strenger Schweizer Bau-Sicherheitsprüfer (SiBe).
                        Deine Aufgabe: Analysiere diese Aufnahmen KRITISCH nach BauAV und SUVA.
                        
                        WICHTIG - Suche gezielt nach LEBENSGEFAHR:
                        1. GRÄBEN: Steht ein Bagger im Graben? Sind Wände senkrecht (>1.5m) ohne Spriessung? (BauAV Art 19/20)
                        2. ARMIERUNG: Ragen Eisen heraus ohne Schutzkappen? (Aufspiessgefahr)
                        3. ABSTURZ: Fehlen Geländer an Kanten, Treppen oder Grabenübergängen? (BauAV Art 10/14/18)
                        4. ORDNUNG: Liegt Material chaotisch auf Wegen?
                        
                        Sei sehr konkret. Schreibe z.B. "Bagger im ungesicherten Graben" statt nur "Sicherheitsmangel".
                        Finde SO VIELE Mängel wie möglich (keine Begrenzung).
                        
                        Antworte NUR als JSON Liste:
                        [{"kategorie": "...", "prioritaet": "Kritisch/Hoch/Mittel", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                        """
                        
                        # Versuche verschiedene Modellnamen für Gemini 3.0
                        model_names = ['gemini-3-pro-preview', 'gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-pro']
                        res = None
                        used_model = None
                        
                        for model_name in model_names:
                            try:
                                model = genai.GenerativeModel(model_name)
                                
                                if st.session_state.m_type == "video":
                                    f = genai.upload_file(st.session_state.m_files[0])
                                    while f.state.name == "PROCESSING": time.sleep(1)
                                    res = model.generate_content([f, prompt], generation_config={"response_mime_type": "application/json"})
                                else:
                                    # Konvertiere Bilder zu unterstütztem Format (z.B. MPO -> JPEG)
                                    converted_files = []
                                    temp_files_to_cleanup = []
                                    for p in st.session_state.m_files:
                                        converted = convert_image_to_supported_format(p)
                                        if converted != p:
                                            temp_files_to_cleanup.append(converted)
                                        converted_files.append(converted)
                                    
                                    # Öffne konvertierte Bilder
                                    imgs = [Image.open(p) for p in converted_files]
                                    res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                                    
                                    # Aufräumen: Lösche temporäre konvertierte Dateien
                                    for temp_file in temp_files_to_cleanup:
                                        try:
                                            if os.path.exists(temp_file):
                                                os.remove(temp_file)
                                        except:
                                            pass
                                
                                used_model = model_name
                                if model_name != 'gemini-3-pro-preview':
                                    st.info(f"ℹ️ Verwende {model_name} (Gemini 3.0 nicht verfügbar)")
                                break
                            except Exception as e:
                                if "404" in str(e) or "not found" in str(e).lower():
                                    continue  # Versuche nächstes Modell
                                else:
                                    raise  # Anderer Fehler, weiterwerfen
                        
                        if res is None:
                            raise Exception("Kein verfügbares Modell gefunden. Bitte API-Key und Modellverfügbarkeit überprüfen.")
                        
                        st.session_state.analysis_data = json.loads(clean_json(res.text))
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Fehler: {e}")
                        if st.button("Nochmal versuchen"): st.rerun()

            if st.session_state.analysis_data:
                st.success(f"⚠️ {len(st.session_state.analysis_data)} Mängel gefunden")
                
                # --- HIER SIND DIE NEUEN EINGABEFELDER ---
                st.markdown("### 📝 Projektdaten für Bericht")
                col_a, col_b = st.columns(2)
                with col_a:
                    proj = st.text_input("Projektname", value="Überbauung 'Luegisland', Wohlen AG")
                    insp = st.text_input("Inspektor Name", value="Dominik Marti")
                with col_b:
                    stat = st.selectbox("Status", ["⚠️ Massnahmen erforderlich", "✅ In Ordnung", "🛑 Kritisch - Baustopp"])
                
                st.divider()
                st.markdown("### Mängel Auswahl")
                # -----------------------------------------

                with st.form("check"):
                    confirmed = []
                    # ... (hier bleibt deine Schleife für die Mängel gleich wie vorher) ...
                    for i, item in enumerate(st.session_state.analysis_data):
                        # ... (Dein existierender Code für Bilder/Text) ...
                        # Nur zur Orientierung, das hier nicht kopieren, wenn es schon da ist:
                        c1, c2 = st.columns([1,3])
                        with c1:
                             if st.session_state.m_type == "video":
                                frm = extract_frame(st.session_state.m_files[0], item.get('zeitstempel_sekunden', 0))
                                if frm is not None: st.image(frm)
                             else:
                                idx = item.get('bild_index', 0)
                                if idx < len(st.session_state.m_files): st.image(st.session_state.m_files[idx])
                        with c2:
                            st.markdown(f"#### :orange[{i+1}. {item['mangel']}]")
                            st.caption(item.get('verstoss'))
                            st.write(item.get('massnahme'))
                            if st.checkbox("Aufnehmen", True, key=str(i)): confirmed.append(item)
                        st.divider()

                    if st.form_submit_button("Berichte erstellen"):
                        st.session_state.final = confirmed
                        # WICHTIG: Wir speichern die Eingaben in session_state
                        st.session_state.meta_projekt = proj
                        st.session_state.meta_inspektor = insp
                        st.session_state.meta_status = stat
                        
                        st.session_state.app_step = 'screen_c'
                        st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("Fertig!")
            
            # Daten holen
            p_name = st.session_state.get('meta_projekt', 'Unbekannt')
            i_name = st.session_state.get('meta_inspektor', 'Unbekannt')
            s_text = st.session_state.get('meta_status', 'Offen')

            # PDF Generierung (Mit neuen Argumenten!)
            pdf_file = create_pdf(st.session_state.final, st.session_state.m_type, st.session_state.m_files, p_name, i_name, s_text)
            
            col1, col2 = st.columns(2)
            with col1:
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 PDF Bericht", f, "SSD_Bericht.pdf", mime="application/pdf")
            
            with col2:
                if WORD_AVAILABLE:
                    # Word Generierung (Mit neuen Argumenten!)
                    word_file = create_word(st.session_state.final, st.session_state.m_type, st.session_state.m_files, p_name, i_name, s_text)
                    with open(word_file, "rb") as f:
                        st.download_button("📝 Word Bericht", f, "SSD_Bericht.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                else:
                    st.error("Word-Export geht nicht. Hast du 'python-docx' in requirements.txt eingetragen?")

            if st.button("Neuer Auftrag"):
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.session_state.m_files = []
                st.rerun()

elif st.session_state.current_page == 'suva':
    # SUVA REGELN
    st.header("📋 SUVA Regeln")
    st.write("Hier finden Sie die wichtigsten SUVA-Regeln für die Baustellensicherheit.")
    
    regel_files = [f"regel_{i}.png" for i in range(1, 9)]
    for regel_file in regel_files:
        if os.path.exists(regel_file):
            st.image(regel_file, use_container_width=True)
            st.markdown("---")

elif st.session_state.current_page == 'bauav':
    # BAUAV
    st.header("⚖️ BauAV (Bauarbeitenverordnung)")
    st.write("Hier finden Sie die wichtigsten BauAV-Regeln für die Baustellensicherheit.")
    
    regel_files = [f"regel_{i}.png" for i in range(1, 9)]
    for regel_file in regel_files:
        if os.path.exists(regel_file):
            st.image(regel_file, use_container_width=True)
            st.markdown("---")
