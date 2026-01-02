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
USER_DB_FILE = "users.json"

# ==========================================
# 1. USER MANAGEMENT
# ==========================================
def load_users():
    if not os.path.exists(USER_DB_FILE):
        default_db = {"admin": "1234"}
        with open(USER_DB_FILE, "w") as f: json.dump(default_db, f)
        return default_db
    try:
        with open(USER_DB_FILE, "r") as f: return json.load(f)
    except:
        return {"admin": "1234"}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        with open(USER_DB_FILE, "w") as f: json.dump(users, f)

# ==========================================
# 2. HILFSFUNKTIONEN
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
    pdf.cell(0, 5, f"Datum: {date.today().strftime('%d.%m.%Y')} | KI-Analyse: Gemini 2.5 Flash", ln=True)
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

# STATE INITIALISIERUNG
if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None

# ==========================================
# 3. SIDEBAR MENÜ
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    st.title("Menü")
    options = ["🏠 Home", "🛡️ SafeSite-Check", "📚 BauAV Nachschlagewerk", "📋 8 Lebenswichtige Regeln"]
    if st.session_state.logged_in and st.session_state.current_user == "admin":
        options.append("👥 Kundenverwaltung")
        
    menu = st.radio("Navigation", options)
    
    st.divider()
    if menu == "🛡️ SafeSite-Check" and st.session_state.logged_in:
        if st.button("🔄 Reset Auftrag"):
            st.session_state.step = 1
            st.session_state.data = []
            st.rerun()

# ==========================================
# 4. HAUPTBEREICH
# ==========================================
if os.path.exists(TITELBILD_FILE):
    st.image(TITELBILD_FILE, use_container_width=True)
st.title("SafeSite Drohne")

# --- LOGIN ---
if not st.session_state.logged_in:
    st.info("Bitte anmelden.")
    col1, col2 = st.columns([1,2])
    with col1:
        u = st.text_input("Benutzername")
        p = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Falsch.")

else:
    # --- APP START ---
    if menu == "🏠 Home":
        st.info(f"Willkommen zurück, {st.session_state.current_user}!")
        st.write("Starten Sie einen neuen Auftrag über das Menü links.")
        col1, col2, col3 = st.columns(3)
        with col1: st.link_button("📸 Instagram", "https://instagram.com")
        with col2: st.link_button("👍 Facebook", "https://facebook.com")
        with col3: st.link_button("🌍 Webseite", "https://safesitedrohne.ch")

    elif menu == "🛡️ SafeSite-Check":
        if st.session_state.step == 1:
            st.subheader("Neuer Auftrag")
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
            st.subheader("🕵️‍♂️ KI-Scanner läuft...")
            if st.session_state.type == "video": st.video(st.session_state.files[0])
            else:
                cols = st.columns(3)
                for i,f in enumerate(st.session_state.files): 
                    with cols[i%3]: st.image(f, caption=f"Bild {i+1}")

            if not st.session_state.data:
                with st.spinner("Suche Mängel (Modell: Gemini 2.5 Flash)..."):
                    try:
                        genai.configure(api_key=API_KEY)
                        
                        # --- HIER IST DEIN GEWÜNSCHTER FIX ---
                        try:
                            # Wir versuchen ERST dein "Wundermodell"
                            model = genai.GenerativeModel('gemini-2.5-flash')
                        except:
                            # Falls Google es heute nicht kennt, nehmen wir den stabilen Klassiker
                            model = genai.GenerativeModel('gemini-pro')
                        
                        prompt = """
                        Du bist Schweizer Bau-Sicherheitsexperte (SiBe).
                        Analysiere die Aufnahmen streng nach BauAV/SUVA.
                        WICHTIG:
                        1. Finde ALLE sichtbaren Mängel (mindestens 5-10, wenn vorhanden).
                        2. Ignoriere Limits. Liste alles auf.
                        3. Achte auf: Absturz, Gräben, PSA, Gerüste.
                        Antworte NUR als JSON Liste:
                        [{"mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                        """
                        
                        if st.session_state.type == "video":
                            f = genai.upload_file(st.session_state.files[0])
                            # Warteschleife (wichtig!)
                            while f.state.name == "PROCESSING":
                                time.sleep(2)
                                f = genai.get_file(f.name)
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
                            st.markdown(f"#### :orange[{i+1}. {item['mangel']}]")
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

    elif menu == "👥 Kundenverwaltung":
        st.subheader("Benutzer verwalten")
        users = load_users()
        with st.form("new_user"):
            nu = st.text_input("Name")
            np = st.text_input("Passwort")
            if st.form_submit_button("Speichern"):
                if nu and np:
                    save_user(nu, np)
                    st.rerun()
        st.divider()
        for user in users:
            st.write(f"👤 {user}")
            if user != "admin" and st.button(f"Löschen {user}"):
                delete_user(user)
                st.rerun()

    elif menu == "📚 BauAV Nachschlagewerk":
        st.subheader("📚 BauAV Datenbank")
        def bauav_card(titel, art, inhalt):
            with st.container(border=True):
                st.markdown(f"#### :orange[{titel}] <span style='color:grey; font-size:0.8em'>({art})</span>", unsafe_allow_html=True)
                st.write(inhalt)
        bauav_card("Absturzsicherung", "Art. 18 ff.", "Ab 2.00m Absturzhöhe zwingend Seitenschutz.")
        bauav_card("Gräben", "Art. 68 ff.", "Ab 1.50m Tiefe spriessen.")
        bauav_card("PSA", "Art. 6", "Helmtragepflicht.")

    elif menu == "📋 8 Lebenswichtige Regeln":
        st.subheader("🇨🇭 SUVA Regeln")
        regeln = [
            {"t": "Absturzkanten", "txt": "Ab 2m sichern.", "img": "regel_1.png"},
            {"t": "Öffnungen", "txt": "Abdecken.", "img": "regel_2.png"},
            {"t": "Lasten", "txt": "Sicher anschlagen.", "img": "regel_3.png"},
            {"t": "Gerüste", "txt": "Täglich prüfen.", "img": "regel_4.png"},
            {"t": "Gerüstzugang", "txt": "Treppen nutzen.", "img": "regel_5.png"},
            {"t": "Zugänge", "txt": "Sichern.", "img": "regel_6.png"},
            {"t": "PSA", "txt": "Helm tragen.", "img": "regel_7.png"},
            {"t": "Gräben", "txt": "Spriessen.", "img": "regel_8.png"},
        ]
        for r in regeln:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                with c1:
                    if os.path.exists(r["img"]): st.image(r["img"])
                with c2:
                    st.markdown(f"#### :orange[{r['t']}]")
                    st.write(r["txt"])
