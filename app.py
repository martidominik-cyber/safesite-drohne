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
from docx import Document
from docx.shared import Inches

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
        self.set_text_color(255, 102, 0)
        self.cell(0, 10, 'Sicherheitsbericht', ln=True)
        self.ln(10)

def create_pdf(data, m_type, m_files):
    pdf = PDF(); pdf.add_page()
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0,0,0)
    pdf.cell(0, 10, f"Gefundene Mängel: {len(data)}", ln=True); pdf.ln(5)
    
    for i, item in enumerate(data):
        if pdf.get_y() > 230: pdf.add_page()
        pdf.set_font("Arial", 'B', 11); pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, f"{i+1}. {item.get('mangel', 'Mangel')}", ln=True)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
        pdf.multi_cell(0, 5, f"Verstoss: {item.get('verstoss')}\nMassnahme: {item.get('massnahme')}")
        pdf.ln(2)
        
        img_path = None
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_{i}.jpg"
                cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
            
        if img_path:
            try: pdf.image(img_path, x=15, w=120)
            except: pass
            pdf.ln(5)
            if m_type == "video" and img_path.startswith("temp"): os.remove(img_path)
            
    out = "Bericht.pdf"
    pdf.output(out)
    return out

# --- WORD GENERATOR (NEU) ---
def create_word(data, m_type, m_files):
    doc = Document()
    doc.add_heading('Sicherheitsbericht SafeSite', 0)
    doc.add_paragraph(f"Datum: {date.today().strftime('%d.%m.%Y')}")
    
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('mangel', 'Mangel')}", level=1)
        
        p = doc.add_paragraph()
        runner = p.add_run("Verstoss: ")
        runner.bold = True
        p.add_run(f"{item.get('verstoss')}\n")
        
        runner = p.add_run("Massnahme: ")
        runner.bold = True
        p.add_run(f"{item.get('massnahme')}")
        
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
            try:
                doc.add_picture(img_path, width=Inches(5))
            except: pass
            
            if temp_created and os.path.exists(img_path):
                os.remove(img_path)

    out = "Bericht.docx"
    doc.save(out)
    return out

# ==========================================
# 2. APP OBERFLÄCHE
# ==========================================
if 'app_step' not in st.session_state: st.session_state.app_step = 'screen_a'
if 'analysis_data' not in st.session_state: st.session_state.analysis_data = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# SIDEBAR
with st.sidebar:
    st.title("SafeSite Drohne")
    if st.session_state.logged_in:
        if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# LOGIN
if not st.session_state.logged_in:
    st.header("Login")
    u = st.text_input("User"); p = st.text_input("Passwort", type="password")
    if st.button("Einloggen"):
        users = load_users()
        if u in users and users[u] == p:
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Falsch")

else:
    # HAUPT APP
    if st.session_state.app_step == 'screen_a':
        st.subheader("Neuer Auftrag")
        
        mode = st.radio("Quelle:", ["📹 Video", "📸 Fotos"], horizontal=True)
        files = []
        
        if mode == "📹 Video":
            vf = st.file_uploader("Video", type=["mp4"])
            if vf and st.button("Analyse starten"):
                t = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); t.write(vf.read()); files.append(t.name); t.close()
                st.session_state.m_type = "video"; st.session_state.m_files = files; st.session_state.app_step = 'screen_b'; st.rerun()
        else:
            pf = st.file_uploader("Fotos", type=["jpg", "png"], accept_multiple_files=True)
            if pf and st.button("Analyse starten"):
                for f in pf:
                    t = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg'); t.write(f.read()); files.append(t.name); t.close()
                st.session_state.m_type = "images"; st.session_state.m_files = files; st.session_state.app_step = 'screen_b'; st.rerun()

    elif st.session_state.app_step == 'screen_b':
        st.subheader("🕵️‍♂️ KI scannt Baustelle...")
        
        if st.session_state.m_type == "video": 
            st.video(st.session_state.m_files[0])
        else: 
            cols = st.columns(3)
            for i, f in enumerate(st.session_state.m_files):
                with cols[i % 3]:
                    st.image(f, caption=f"Bild {i+1}")

        if not st.session_state.analysis_data:
            with st.spinner("Analyse läuft..."):
                try:
                    genai.configure(api_key=API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = """
                    Du bist Schweizer Bau-Sicherheitsexperte (SiBe).
                    Analysiere die Aufnahmen streng nach BauAV/SUVA.
                    
                    WICHTIG:
                    - Finde ALLE sichtbaren Mängel (begrenze dich NICHT auf 3).
                    - Liste so viele wie möglich auf.
                    - Achte auf: Absturzsicherung, PSA (Helme), Gräben, Gerüste.
                    
                    Gib das Ergebnis NUR als JSON Array zurück:
                    [{"kategorie": "...", "prioritaet": "Hoch/Mittel", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                    """
                    
                    if st.session_state.m_type == "video":
                        f = genai.upload_file(st.session_state.m_files[0])
                        while f.state.name == "PROCESSING": time.sleep(1)
                        res = model.generate_content([f, prompt], generation_config={"response_mime_type": "application/json"})
                    else:
                        imgs = [Image.open(p) for p in st.session_state.m_files]
                        res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                    
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
                        st.markdown(f"**{item.get('mangel')}**")
                        st.caption(f"Verstoss: {item.get('verstoss')}")
                        if st.checkbox("Aufnehmen", True, key=str(i)): confirmed.append(item)
                    st.divider()
                
                if st.form_submit_button("Berichte erstellen"):
                    st.session_state.confirmed = confirmed
                    st.session_state.app_step = 'screen_c'
                    st.rerun()

    elif st.session_state.app_step == 'screen_c':
        st.subheader("Fertig!")
        if st.session_state.confirmed:
            
            # PDF Erstellen
            pdf_file = create_pdf(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files)
            
            # Word Erstellen
            word_file = create_word(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files)
            
            col1, col2 = st.columns(2)
            with col1:
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 PDF Herunterladen", f, "Bericht.pdf", mime="application/pdf")
            with col2:
                with open(word_file, "rb") as f:
                    st.download_button("📝 Word Herunterladen", f, "Bericht.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        if st.button("Neuer Auftrag"):
            st.session_state.app_step = 'screen_a'
            st.session_state.analysis_data = []
            st.session_state.m_files = []
            st.rerun()
