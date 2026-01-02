import streamlit as st
import google.generativeai as genai
import cv2
import tempfile
import os
import json
from fpdf import FPDF
import time
from datetime import date
import urllib.parse
from PIL import Image

# ==========================================
# 0. SETUP & KONFIGURATION
# ==========================================
st.set_page_config(page_title="SafeSite Drohne", page_icon="logo.jpg", layout="wide", initial_sidebar_state="auto")

# ----------------------------------------------------
# 🔴 HIER DEINEN GITHUB-LINK EINFÜGEN!
LOGO_URL_GITHUB = "https://raw.githubusercontent.com/martidominik-cyber/safesite-drohne/main/logo.jpg?v=1"
# ----------------------------------------------------

# DESIGN & CSS
st.markdown(f"""
<style>
    .stAppDeployButton {{display: none;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebarCollapsedControl"] {{color: #FF6600 !important;}}
</style>

<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default"> 

<link rel="apple-touch-icon" href="{LOGO_URL_GITHUB}">
<link rel="apple-touch-icon" sizes="152x152" href="{LOGO_URL_GITHUB}">
<link rel="apple-touch-icon" sizes="180x180" href="{LOGO_URL_GITHUB}">
<link rel="icon" type="image/png" href="{LOGO_URL_GITHUB}">
""", unsafe_allow_html=True)

# 🔒 DATEI FÜR BENUTZERDATEN
USER_DB_FILE = "users.json"

# --- USER MANAGEMENT ---
def load_users():
    if not os.path.exists(USER_DB_FILE):
        default_users = {"admin": "1234"} 
        with open(USER_DB_FILE, "w") as f:
            json.dump(default_users, f)
        return default_users
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

# 🔴 API KEY LADEN
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # HIER KEY EINFÜGEN FÜR LOKALES TESTEN
    API_KEY = "DEIN_API_KEY_HIER_EINFÜGEN"

LOGO_FILE = "logo.jpg" 
TITELBILD_FILE = "titelbild.png" 

# --- STYLING ---
st.markdown("""
<style>
    :root { --primary: #FF6600; --dark: #333333; }
    .stButton > button {
        background-color: #FF6600 !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        border: 2px solid #CC5200 !important;
        width: 100%;
        height: 80px;
        margin-bottom: 20px;
    }
    .stButton > button:hover {
        background-color: #CC5200 !important;
        border-color: #993D00 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. STATUS MANAGEMENT
# ==========================================
if 'app_step' not in st.session_state:
    st.session_state.app_step = 'screen_a' 
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = [] 
if 'media_type' not in st.session_state:
    st.session_state.media_type = "video" 
if 'media_files' not in st.session_state:
    st.session_state.media_files = [] 
if 'confirmed_items' not in st.session_state:
    st.session_state.confirmed_items = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# ==========================================
# 2. HILFS-FUNKTIONEN
# ==========================================

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 10, 8, 40)
            except: pass
        self.set_font('Arial', 'B', 16)
        self.set_xy(60, 15)
        self.set_text_color(255, 102, 0)
        self.cell(0, 10, 'Sicherheitsbericht & Mängelprotokoll', ln=True)
        self.set_font('Arial', '', 9)
        self.set_xy(60, 25)
        self.set_text_color(0, 0, 0)
        heute = date.today().strftime("%d.%m.%Y")
        self.cell(0, 5, f"Datum: {heute} | Basis: BauAV & SUVA | KI-Analyse (Pro-Modell)", ln=True)
        self.ln(15)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'R')

def clean_json_string(text):
    text = text.strip()
    if text.startswith("```json"): text = text[7:]
    if text.endswith("```"): text = text[:-3]
    return text.strip()

def extract_frame(video_path, timestamp):
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()
        if ret: return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except: return None
    return None

def create_smart_pdf(data_list, media_type, media_files):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Gefundene Mängel (Detailliste):", ln=True)
    pdf.ln(5)

    for idx, item in enumerate(data_list):
        if pdf.get_y() > 220: pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(204, 0, 0) 
        titel = f"{idx+1}. {item.get('kategorie', 'Allgemein')} (Priorität: {item.get('prioritaet', 'Mittel')})"
        pdf.cell(0, 8, titel.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        
        mangel = item.get('mangel', '-')
        verstoss = item.get('verstoss', '-')
        massnahme = item.get('massnahme', '-')
        
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Mangel: "); pdf.set_font("Arial", '', 10); pdf.write(5, mangel.encode('latin-1', 'replace').decode('latin-1')); pdf.ln(6)
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Verstoss: "); pdf.set_font("Arial", '', 10); pdf.write(5, verstoss.encode('latin-1', 'replace').decode('latin-1')); pdf.ln(6)
        pdf.set_font("Arial", 'B', 10); pdf.write(5, "Massnahme: "); pdf.set_font("Arial", '', 10); pdf.write(5, massnahme.encode('latin-1', 'replace').decode('latin-1')); pdf.ln(8)

        image_path_for_pdf = None
        temp_created = False

        if media_type == "video":
            video_path = media_files[0]
            img = extract_frame(video_path, item.get('zeitstempel_sekunden', 0))
            if img is not None:
                image_path_for_pdf = f"temp_{idx}.jpg"
                cv2.imwrite(image_path_for_pdf, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                temp_created = True
        elif media_type == "images":
            img_index = item.get('bild_index', 0)
            if img_index < len(media_files):
                image_path_for_pdf = media_files[img_index]

        if image_path_for_pdf and os.path.exists(image_path_for_pdf):
            try: pdf.image(image_path_for_pdf, x=20, w=140)
            except: pass
            pdf.ln(5)
            if media_type == "video":
                pdf.set_font("Arial", 'I', 8)
                pdf.cell(0, 5, f"Abb: Szene bei Sekunde {item.get('zeitstempel_sekunden', 0)}", ln=True, align='C')
            pdf.ln(10)
        
        if temp_created and image_path_for_pdf:
            try: os.remove(image_path_for_pdf)
            except: pass

    out = "SSD_Bericht.pdf"
    pdf.output(out)
    return out

# ==========================================
# 3. SIDEBAR & START
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🔓 Abmelden"):
            st.session_state.logged_in = False
            st.rerun()
    st.title("Menü")
    menu_options = ["🏠 Home", "🛡️ SafeSite-Check"]
    selected_mode = st.radio("Wähle Ansicht:", menu_options)
    st.divider()
    if selected_mode == "🛡️ SafeSite-Check" and st.session_state.logged_in:
        if st.button("🔄 Check Neustarten"):
            st.session_state.app_step = 'screen_a'
            st.session_state.analysis_data = []
            st.session_state.media_files = []
            st.rerun()

if os.path.exists(TITELBILD_FILE): st.image(TITELBILD_FILE, use_container_width=True)
st.markdown("<h1 style='text-align: center; color: #FF6600;'>SafeSite Drohne</h1>", unsafe_allow_html=True)

if selected_mode == "🏠 Home":
    st.info("Bitte links SafeSite-Check wählen.")

elif selected_mode == "🛡️ SafeSite-Check":
    if not st.session_state.logged_in:
        st.subheader("🔒 Login")
        u = st.text_input("User"); p = st.text_input("Pass", type="password")
        if st.button("Login"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
    else:
        # --- APP FLOW ---
        if st.session_state.app_step == 'screen_a':
            st.subheader("Neuer Auftrag")
            st.markdown("### Modus wählen")
            mode = st.radio("", ["📹 Video", "📸 Fotos"], horizontal=True)
            
            files = []
            if mode == "📹 Video":
                vf = st.file_uploader("Video (mp4)", type=["mp4"])
                if vf and st.button("Analyse (Pro-Mode) starten"):
                    t = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); t.write(vf.read()); files.append(t.name); t.close()
                    st.session_state.media_type = "video"; st.session_state.media_files = files; st.session_state.app_step = 'screen_b'; st.rerun()
            else:
                pf = st.file_uploader("Fotos (jpg/png)", type=["jpg","png"], accept_multiple_files=True)
                if pf and st.button("Analyse (Pro-Mode) starten"):
                    for f in pf:
                        t = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg'); t.write(f.read()); files.append(t.name); t.close()
                    st.session_state.media_type = "images"; st.session_state.media_files = files; st.session_state.app_step = 'screen_b'; st.rerun()

        elif st.session_state.app_step == 'screen_b':
            st.subheader("🔍 Analyse (Gemini 1.5 Pro)")
            media_type = st.session_state.media_type
            media_files = st.session_state.media_files
            
            if media_type == "video": st.video(media_files[0])
            else: 
                cols = st.columns(3)
                for i,p in enumerate(media_files): 
                    with cols[i%3]: st.image(p, caption=f"Bild {i}")

            if not st.session_state.analysis_data:
                status = st.status("🤖 KI denkt nach (Pro-Modell)... Das dauert etwas länger.", expanded=True)
                try:
                    if "HIER_EINFÜGEN" in API_KEY: st.error("API Key fehlt!")
                    else:
                        genai.configure(api_key=API_KEY)
                        # HIER IST DER WECHSEL AUF DAS PRO MODELL!
                        model = genai.GenerativeModel('gemini-1.5-pro') 
                        
                        # DER PROMPT IST JETZT EINE CHECKLISTE
                        checklist_prompt = """
                        Du bist ein strenger Schweizer Bau-Sicherheitsexperte (SiBe).
                        Analysiere das Bildmaterial GENAU nach BauAV und SUVA Regeln.
                        Gehe wie folgt vor (Checkliste):
                        1. ABSTURZSICHERUNG: Fehlen Seitenschutz/Geländer an Kanten (>2m)? Sind Öffnungen offen?
                        2. GERÜSTE: Fehlen Bordbretter? Sind Beläge lückenhaft? Fehlen Verankerungen?
                        3. GRÄBEN: Sind Gräben (>1.5m) ungesichert? Fehlen Zugänge?
                        4. PSA: Tragen ALLE Arbeiter Helme? Warnwesten?
                        5. LEITERN: Sind Leitern ungesichert oder kaputt?
                        
                        Gib JEDEN Verstoß aus, den du findest (auch kleine). Sei kritisch!
                        Ignoriere die Begrenzung auf 3. Finde so viele wie da sind.
                        
                        JSON Format: 
                        [{"kategorie": "...", "prioritaet": "Hoch/Mittel", "mangel": "...", "verstoss": "BauAV Art. ...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                        """
                        
                        if media_type == "video":
                            vf = genai.upload_file(media_files[0])
                            while vf.state.name == "PROCESSING": time.sleep(1)
                            res = model.generate_content([vf, checklist_prompt], generation_config={"response_mime_type": "application/json"})
                        else:
                            imgs = [Image.open(p) for p in media_files]
                            res = model.generate_content([checklist_prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                        
                        st.session_state.analysis_data = json.loads(clean_json_string(res.text))
                        status.update(label="Fertig!", state="complete")
                except Exception as e: st.error(f"Fehler: {e}")

            if st.session_state.analysis_data:
                with st.form("val"):
                    confirmed = []
                    for i, item in enumerate(st.session_state.analysis_data):
                        c1, c2 = st.columns([1,2])
                        with c1:
                            if media_type == "video":
                                img = extract_frame(media_files[0], item.get('zeitstempel_sekunden', 0))
                                if img: st.image(img)
                            else:
                                idx = item.get('bild_index', 0)
                                if idx < len(media_files): st.image(media_files[idx])
                        with c2:
                            st.error(f"{item.get('mangel')}")
                            st.caption(item.get('verstoss'))
                            if st.checkbox("Aufnehmen", True, key=f"c{i}"): confirmed.append(item)
                        st.divider()
                    if st.form_submit_button("Bericht erstellen"):
                        st.session_state.confirmed_items = confirmed
                        st.session_state.app_step = 'screen_c'
                        st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("Bericht fertig")
            if st.session_state.confirmed_items:
                pdf = create_smart_pdf(st.session_state.confirmed_items, st.session_state.media_type, st.session_state.media_files)
                with open(pdf, "rb") as f: st.download_button("PDF Download", f, "Bericht.pdf")
            if st.button("Neuer Auftrag"):
                st.session_state.app_step = 'screen_a'; st.session_state.analysis_data = []; st.session_state.media_files = []; st.rerun()
