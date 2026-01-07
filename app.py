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

# --- PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 102, 0) # Orange
        self.cell(0, 10, 'Sicherheitsbericht (Pro-Analyse)', ln=True)
        self.ln(5)

def create_pdf(data, m_type, m_files):
    pdf = PDF(); pdf.add_page()
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0,0,0)
    pdf.cell(0, 10, f"Gefundene Mängel: {len(data)}", ln=True); pdf.ln(5)
    
    for i, item in enumerate(data):
        if pdf.get_y() > 220: pdf.add_page()
        
        # Titel Rot und Fett
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(204, 0, 0)
        titel = f"{i+1}. {item.get('kategorie', 'Mangel')} ({item.get('prioritaet', 'Mittel')})"
        pdf.cell(0, 8, titel.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Text Schwarz
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
        
        # Mangel
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Situation: ")
        pdf.set_font("Arial", '', 10); pdf.write(5, item.get('mangel', '-').encode('latin-1', 'replace').decode('latin-1')); pdf.ln(6)
        
        # Verstoss
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Verstoss: ")
        pdf.set_font("Arial", '', 10); pdf.write(5, item.get('verstoss', '-').encode('latin-1', 'replace').decode('latin-1')); pdf.ln(6)
        
        # Massnahme
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Massnahme: ")
        pdf.set_font("Arial", '', 10); pdf.write(5, item.get('massnahme', '-').encode('latin-1', 'replace').decode('latin-1')); pdf.ln(8)
        
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
            
    out = "Bericht.pdf"
    pdf.output(out)
    return out

# --- WORD GENERATOR ---
def create_word(data, m_type, m_files):
    if not WORD_AVAILABLE: return None
    doc = Document()
    doc.add_heading('Sicherheitsbericht SafeSite', 0)
    doc.add_paragraph(f"Datum: {date.today().strftime('%d.%m.%Y')} | KI-Modell: Gemini 3.0 Pro")
    
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('kategorie', 'Mangel')}", level=1)
        
        p = doc.add_paragraph()
        p.add_run("Priorität: ").bold = True
        p.add_run(f"{item.get('prioritaet')}\n")
        
        p.add_run("Situation/Mangel: ").bold = True
        p.add_run(f"{item.get('mangel')}\n")
        
        p.add_run("Verstoss: ").bold = True
        p.add_run(f"{item.get('verstoss')}\n")
        
        p.add_run("Massnahme: ").bold = True
        p.add_run(f"{item.get('massnahme')}")
        
        # Bild
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
            try: doc.add_picture(img_path, width=Inches(5))
            except: pass
            if temp_created and os.path.exists(img_path): os.remove(img_path)

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
    page = st.radio(
        "Bereich wählen:",
        ["🏠 Startseite", "🔍 SafeSite-Check"],
        index=0 if st.session_state.current_page == 'home' else 1,
        key="nav"
    )
    
    if page == "🏠 Startseite":
        st.session_state.current_page = 'home'
    elif page == "🔍 SafeSite-Check":
        st.session_state.current_page = 'safesite'
    
    # Logout nur anzeigen, wenn im SafeSite-Check eingeloggt
    if st.session_state.current_page == 'safesite' and st.session_state.logged_in:
        st.divider()
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()
    
    # SUVA REGELN & BAUAV
    st.divider()
    st.subheader("📋 SUVA Regeln & BauAV")
    
    # Erweiterbarer Bereich für die Regeln
    with st.expander("Regeln anzeigen", expanded=False):
        regel_files = [f"regel_{i}.png" for i in range(1, 9)]
        for regel_file in regel_files:
            if os.path.exists(regel_file):
                st.image(regel_file, use_container_width=True)
                st.markdown("---")

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
                                    imgs = [Image.open(p) for p in st.session_state.m_files]
                                    res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                                
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
                
                with st.form("check"):
                    confirmed = []
                    for i, item in enumerate(st.session_state.analysis_data):
                        c1, c2 = st.columns([1,3])
                        with c1:
                            if st.session_state.m_type == "video":
                                frm = extract_frame(st.session_state.m_files[0], item.get('zeitstempel_sekunden', 0))
                                if frm is not None: st.image(frm)
                            else:
                                idx = item.get('bild_index', 0)
                                if idx < len(st.session_state.m_files): st.image(st.session_state.m_files[idx])
                        with c2:
                            prio = item.get('prioritaet', 'Mittel')
                            color = "red" if prio in ["Kritisch", "Hoch"] else "orange"
                            st.markdown(f":{color}[**{prio}: {item.get('mangel')}**]")
                            st.write(f"⚖️ {item.get('verstoss')}")
                            st.write(f"🛡️ {item.get('massnahme')}")
                            if st.checkbox("In Bericht aufnehmen", True, key=str(i)): confirmed.append(item)
                        st.divider()
                    
                    if st.form_submit_button("Berichte erstellen"):
                        st.session_state.confirmed = confirmed
                        st.session_state.app_step = 'screen_c'
                        st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("Berichte fertig!")
            if st.session_state.confirmed:
                
                # PDF Generierung
                pdf_file = create_pdf(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files)
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 PDF Bericht", f, "SSD_Bericht.pdf", mime="application/pdf")
                
                # Word Generierung (Nur wenn verfügbar)
                if WORD_AVAILABLE:
                    word_file = create_word(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files)
                    if word_file:
                        with open(word_file, "rb") as f:
                            st.download_button("📝 Word Bericht (Editierbar)", f, "SSD_Bericht.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                else:
                    st.error("Word-Export geht nicht. Hast du 'python-docx' in requirements.txt eingetragen?")

            if st.button("Neuer Auftrag"):
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.session_state.m_files = []
                st.rerun()
