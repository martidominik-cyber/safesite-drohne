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

# Word-Modul sicher laden
try:
    from docx import Document
    from docx.shared import Inches
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False

# ==========================================
# 0. KONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="SafeSite Drohne", page_icon="logo.jpg", layout="wide", initial_sidebar_state="expanded")

# --- HIER DEINEN GITHUB-NAMEN EINTRAGEN ---
LOGO_URL_GITHUB = "https://raw.githubusercontent.com/DEIN_BENUTZERNAME/safesite-drohne/main/logo.jpg?v=1"
# ------------------------------------------

# CSS
st.markdown(f"""
<style>
    .stAppDeployButton {{display: none;}}
    footer {{visibility: hidden;}}
    :root {{ --primary: #FF6600; }}
    .stButton > button {{
        background-color: #FF6600 !important;
        color: white !important;
        border: none;
        font-weight: bold;
    }}
</style>
<link rel="apple-touch-icon" href="{LOGO_URL_GITHUB}">
""", unsafe_allow_html=True)

# API KEY
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key fehlt in den Secrets!")
    st.stop()

# DATEIEN
LOGO_FILE = "logo.jpg"
TITELBILD_FILE = "titelbild.png"

# ==========================================
# 1. FUNKTIONEN
# ==========================================
def clean_json(text):
    text = text.strip()
    first = text.find('[')
    last = text.rfind(']')
    if first != -1 and last != -1:
        text = text[first:last+1]
    return text

def extract_frame(video_path, timestamp):
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read(); cap.release()
        if ret: return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except: return None

# PDF
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 10, 8, 30)
            except: pass
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 102, 0)
        self.cell(0, 10, 'Sicherheitsbericht', ln=True, align='C')
        self.ln(10)

def create_pdf(data, m_type, m_files):
    pdf = PDF(); pdf.add_page()
    pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
    pdf.cell(0, 5, f"Datum: {date.today().strftime('%d.%m.%Y')} | KI-Analyse: Gemini 1.5 Pro", ln=True)
    pdf.ln(5)
    
    for i, item in enumerate(data):
        if pdf.get_y() > 230: pdf.add_page()
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(204, 0, 0)
        pdf.cell(0, 8, f"{i+1}. {item.get('mangel', 'Mangel')}", ln=True)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
        pdf.multi_cell(0, 5, f"Verstoss: {item.get('verstoss')}\nMassnahme: {item.get('massnahme')}")
        pdf.ln(3)
        
        img_path = None; temp_created = False
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_{i}.jpg"; cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)); temp_created = True
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
        
        if img_path:
            try: pdf.image(img_path, x=20, w=100)
            except: pass
            pdf.ln(10)
            if temp_created and os.path.exists(img_path): os.remove(img_path)
    out = "SSD_Bericht.pdf"
    pdf.output(out)
    return out

# WORD
def create_word(data, m_type, m_files):
    if not WORD_AVAILABLE: return None
    doc = Document()
    doc.add_heading('Sicherheitsbericht SafeSite', 0)
    doc.add_paragraph(f"Datum: {date.today().strftime('%d.%m.%Y')}")
    
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('mangel')}", level=1)
        p = doc.add_paragraph()
        p.add_run("Verstoss: ").bold = True; p.add_run(f"{item.get('verstoss')}\n")
        p.add_run("Massnahme: ").bold = True; p.add_run(f"{item.get('massnahme')}")
        
        img_path = None; temp_created = False
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_w_{i}.jpg"; cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)); temp_created = True
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
        
        if img_path:
            try: doc.add_picture(img_path, width=Inches(4.5))
            except: pass
            if temp_created and os.path.exists(img_path): os.remove(img_path)
    out = "SSD_Bericht.docx"
    doc.save(out)
    return out

# STATE
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = []

# ==========================================
# 2. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    
    st.title("Menü")
    # Hier sind deine Menüpunkte zurück!
    menu = st.radio("Navigation", [
        "🏠 Home", 
        "🛡️ SafeSite-Check", 
        "📚 BauAV Nachschlagewerk", 
        "📋 8 Lebenswichtige Regeln"
    ])
    
    st.divider()
    if menu == "🛡️ SafeSite-Check":
        if st.button("🔄 Reset"):
            st.session_state.step = 1
            st.session_state.data = []
            st.rerun()

# ==========================================
# 3. HAUPTBEREICH
# ==========================================
if os.path.exists(TITELBILD_FILE):
    st.image(TITELBILD_FILE, use_container_width=True)
st.title("SafeSite Drohne")

# --- HOME ---
if menu == "🏠 Home":
    st.info("Willkommen zurück. Wählen Sie links eine Funktion.")
    col1, col2, col3 = st.columns(3)
    with col1: st.link_button("📸 Instagram", "https://instagram.com")
    with col2: st.link_button("👍 Facebook", "https://facebook.com")
    with col3: st.link_button("🌍 Webseite", "https://safesitedrohne.ch")

# --- CHECK (PRO MODELL) ---
elif menu == "🛡️ SafeSite-Check":
    if st.session_state.step == 1:
        st.subheader("Neuer Auftrag (Pro-Modell)")
        if not WORD_AVAILABLE: st.warning("Word-Export inaktiv (Neustart erforderlich)")

        mode = st.radio("Upload:", ["📹 Video", "📸 Fotos"], horizontal=True)
        files = []
        
        if mode == "📹 Video":
            vf = st.file_uploader("Video (mp4)", type=["mp4"])
            if vf and st.button("Analyse starten 🚀"):
                with st.spinner("Lade Video..."):
                    t = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); t.write(vf.read()); files.append(t.name); t.close()
                    st.session_state.type = "video"; st.session_state.files = files; st.session_state.step = 2; st.rerun()
        else:
            pf = st.file_uploader("Fotos", type=["jpg","png"], accept_multiple_files=True)
            if pf and st.button("Analyse starten 🚀"):
                with st.spinner("Lade Fotos..."):
                    for f in pf:
                        t = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg'); t.write(f.read()); files.append(t.name); t.close()
                    st.session_state.type = "images"; st.session_state.files = files; st.session_state.step = 2; st.rerun()

    elif st.session_state.step == 2:
        st.subheader("🕵️‍♂️ Gemini 1.5 Pro Analyse")
        if st.session_state.type == "video": st.video(st.session_state.files[0])
        else:
            cols = st.columns(3)
            for i,f in enumerate(st.session_state.files): with cols[i%3]: st.image(f, caption=f"Bild {i+1}")

        if not st.session_state.data:
            with st.spinner("Analysiere Baustelle KRITISCH... (kann 30s dauern)"):
                try:
                    genai.configure(api_key=API_KEY)
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    prompt = """
                    Du bist ein strenger Schweizer Bau-Sicherheitsprüfer (SiBe).
                    Analysiere die Bilder/Video KRITISCH nach BauAV und
