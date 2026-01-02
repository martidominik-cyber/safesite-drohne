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
                    Analysiere die Bilder/Video KRITISCH nach BauAV und SUVA.
                    
                    WICHTIG:
                    1. Suche gezielt nach LEBENSGEFAHR:
                       - Gräben ohne Spriessung (>1.5m)? Bagger im Gefahrenbereich?
                       - Fehlende Absturzsicherung?
                       - Armierungseisen ohne Kappen?
                    2. Liste ALLE Mängel auf (kein Limit).
                    3. Sei konkret und professionell.
                    
                    Antworte NUR als JSON Liste:
                    [{"mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                    """
                    if st.session_state.type == "video":
                        f = genai.upload_file(st.session_state.files[0])
                        while f.state.name == "PROCESSING": time.sleep(1)
                        res = model.generate_content([f, prompt], generation_config={"response_mime_type": "application/json"})
                    else:
                        imgs = [Image.open(p) for p in st.session_state.files]
                        res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                    
                    st.session_state.data = json.loads(clean_json(res.text))
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")
                    if st.button("Nochmal"): st.rerun()

        if st.session_state.data:
            st.success(f"{len(st.session_state.data)} Mängel gefunden.")
            with st.form("res"):
                confirmed = []
                for i, item in enumerate(st.session_state.data):
                    c1, c2 = st.columns([1,3])
                    with c1:
                        if st.session_state.type == "video":
                            frm = extract_frame(st.session_state.files[0], item.get('zeitstempel_sekunden', 0))
                            if frm is not None: st.image(frm)
                        else:
                            idx = item.get('bild_index', 0)
                            if idx < len(st.session_state.files): st.image(st.session_state.files[idx])
                    with c2:
                        st.markdown(f"**{i+1}. {item['mangel']}**")
                        st.caption(item.get('verstoss'))
                        st.write(item.get('massnahme'))
                        if st.checkbox("Aufnehmen", True, key=str(i)): confirmed.append(item)
                    st.divider()
                if st.form_submit_button("Berichte erstellen"):
                    st.session_state.final = confirmed
                    st.session_state.step = 3
                    st.rerun()

    elif st.session_state.step == 3:
        st.subheader("Fertig!")
        pdf_file = create_pdf(st.session_state.final, st.session_state.type, st.session_state.files)
        col1, col2 = st.columns(2)
        with col1:
            with open(pdf_file, "rb") as f: st.download_button("📥 PDF", f, "SSD_Bericht.pdf")
        with col2:
            if WORD_AVAILABLE:
                word_file = create_word(st.session_state.final, st.session_state.type, st.session_state.files)
                with open(word_file, "rb") as f: st.download_button("📝 Word", f, "SSD_Bericht.docx")
        
        if st.button("Neuer Auftrag"):
            st.session_state.step = 1; st.session_state.data = []; st.rerun()

# --- BAUAV ---
elif menu == "📚 BauAV Nachschlagewerk":
    st.subheader("📚 BauAV Datenbank")
    
    def bauav_card(titel, art, inhalt):
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #FF6600; margin-bottom: 20px;">
            <h4 style="color: #FF6600; margin:0;">{titel} <span style="font-size:0.8em; color:#666;">({art})</span></h4>
            <p style="margin-top:10px;">{inhalt}</p>
        </div>
        """, unsafe_allow_html=True)

    bauav_card("Absturzsicherung", "Art. 18 ff.", "Ab 2.00m Absturzhöhe zwingend Seitenschutz (Holm, Zwischenholm, Bordbrett).")
    bauav_card("Gräben & Baugruben", "Art. 68 ff.", "Ab 1.50m Tiefe müssen Wände geböscht oder verspriesst werden.")
    bauav_card("Gerüste", "Art. 47 ff.", "Tägliche Sichtkontrolle. Beläge dicht verlegt. Ab 3m Fassadengerüst.")
    bauav_card("PSA", "Art. 6", "Helmtragepflicht und Warnkleidung im Baustellenbereich.")

# --- 8 REGELN ---
elif menu == "📋 8 Lebenswichtige Regeln":
    st.subheader("🇨🇭 Die 8 lebenswichtigen Regeln")
    
    regeln = [
        {"t": "Absturzkanten sichern", "txt": "Absturzhöhe > 2m sichern.", "img": "regel_1.png"},
        {"t": "Bodenöffnungen verschliessen", "txt": "Durchbruchsicher abdecken.", "img": "regel_2.png"},
        {"t": "Lasten anschlagen", "txt": "Kranlasten sicher anschlagen.", "img": "regel_3.png"},
        {"t": "Fassadengerüst", "txt": "Ab 3m Höhe Gerüst nutzen.", "img": "regel_4.png"},
        {"t": "Gerüstkontrolle", "txt": "Täglich prüfen. Keine Änderungen.", "img": "regel_5.png"},
        {"t": "Sichere Zugänge", "txt": "Treppen und Leitern sichern.", "img": "regel_6.png"},
        {"t": "PSA tragen", "txt": "Helm, Schuhe, Weste.", "img": "regel_7.png"},
        {"t": "Gräben sichern", "txt": "Ab 1.50m Tiefe spriessen.", "img": "regel_8.png"},
    ]
    
    for r in regeln:
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                if os.path.exists(r["img"]): st.image(r["img"])
                else: st.info("Bild fehlt")
            with c2:
                st.markdown(f"**{r['t']}**")
                st.write(r["txt"])
