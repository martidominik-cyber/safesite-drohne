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

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f)

# 🔴 API Key sicher laden
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY = "AIzaSyC6VlkfBdItsTWec69GXN2dExTQjlT9LgQ"

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
    .social-link {
        display: inline-block; padding: 10px 20px; margin: 10px;
        color: white !important; background-color: #333;
        text-decoration: none; border-radius: 5px;
        font-weight: bold; text-align: center; width: 100%;
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
    st.session_state.media_type = None # "video" oder "images"
if 'media_files' not in st.session_state:
    st.session_state.media_files = [] # Liste der Dateipfade
if 'confirmed_items' not in st.session_state:
    st.session_state.confirmed_items = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# ==========================================
# 2. HILFS-FUNKTIONEN (PDF & MEDIEN)
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
        self.cell(0, 5, f"Datum: {heute} | Basis: BauAV & SUVA | KI-Analyse", ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'R')

def clean_json_string(text):
    text = text.strip().replace("```json", "").replace("```", "")
    return text.strip()

def extract_frame(video_path, timestamp):
    # Nur für Videos nötig
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
        
        pdf.set_font("Arial", 'B', 10)
        pdf.write(5, "Mangel: ")
        pdf.set_font("Arial", '', 10)
        pdf.write(5, mangel.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(6)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.write(5, "Verstoss: ")
        pdf.set_font("Arial", '', 10)
        pdf.write(5, verstoss.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(6)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.write(5, "Massnahme: ")
        pdf.set_font("Arial", '', 10)
        pdf.write(5, massnahme.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(8)

        # BILD EINFÜGEN (Unterscheidung Video vs. Foto)
        image_path_for_pdf = None
        temp_created = False

        if media_type == "video":
            # Video Frame extrahieren
            video_path = media_files[0]
            img = extract_frame(video_path, item.get('zeitstempel_sekunden', 0))
            if img is not None:
                image_path_for_pdf = f"temp_{idx}.jpg"
                cv2.imwrite(image_path_for_pdf, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                temp_created = True
        elif media_type == "images":
            # Das passende Foto nehmen
            img_index = item.get('bild_index', 0)
            if img_index < len(media_files):
                image_path_for_pdf = media_files[img_index]

        # Bild in PDF packen
        if image_path_for_pdf and os.path.exists(image_path_for_pdf):
            # Wir zentrieren das Bild und machen es max 140 breit
            try:
                pdf.image(image_path_for_pdf, x=20, w=140)
            except:
                pass # Falls Bild kaputt
            pdf.ln(5)
            if media_type == "video":
                pdf.set_font("Arial", 'I', 8)
                pdf.cell(0, 5, f"Abb: Szene bei Sekunde {item.get('zeitstempel_sekunden', 0)}", ln=True, align='C')
            pdf.ln(10)
        
        if temp_created and image_path_for_pdf:
            try: os.remove(image_path_for_pdf)
            except: pass

    if pdf.get_y() > 200: pdf.add_page()
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Freigabe / Unterschriften", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.line(10, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Ort, Datum: ...........................................................", ln=True)
    pdf.ln(15)
    
    y = pdf.get_y()
    pdf.line(10, y, 80, y)
    pdf.text(10, y + 5, "Visum SSD Pilot")
    pdf.line(110, y, 180, y)
    pdf.text(110, y + 5, "Visum Polier / Unternehmer")
    pdf.ln(25)
    y = pdf.get_y()
    pdf.line(10, y, 80, y)
    pdf.text(10, y + 5, "Visum Sicherheitsbeauftragter (SiBe)")
    
    out = "SSD_Bericht.pdf"
    pdf.output(out)
    return out

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.current_user}")
        if st.button("🔓 Abmelden"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    st.title("Menü")
    menu_options = ["🏠 Home", "🛡️ SafeSite-Check", "📚 BauAV Nachschlagewerk", "📋 8 Lebenswichtige Regeln"]
    if st.session_state.logged_in and st.session_state.current_user == "admin":
        menu_options.append("👥 Kundenverwaltung")
    
    selected_mode = st.radio("Wähle Ansicht:", menu_options)
    st.divider()
    if selected_mode == "🛡️ SafeSite-Check" and st.session_state.logged_in:
        if st.button("🔄 Check Neustarten"):
            st.session_state.app_step = 'screen_a'
            st.session_state.analysis_data = []
            st.session_state.media_type = None
            st.session_state.media_files = []
            st.session_state.confirmed_items = []
            st.rerun()
    st.caption("SSD SafeSite App v19.0 (Foto & Video Support)")

# ==========================================
# TITEL
# ==========================================
if os.path.exists(TITELBILD_FILE):
    st.image(TITELBILD_FILE, use_container_width=True)
st.markdown("<h1 style='text-align: center; color: #FF6600; font-size: 40px; margin-bottom: 30px;'>SafeSite Drohne</h1>", unsafe_allow_html=True)

# ==========================================
# LOGIK VERTEILER
# ==========================================

if selected_mode == "🏠 Home":
    st.markdown("""
    <div style="background-color: #E0E0E0; padding: 20px; border-radius: 10px; border-left: 5px solid #FF6600; margin-bottom: 30px;">
        <h2 style="color: #FF6600; margin-top: 0;">Willkommen bei SafeSite Drohne</h2>
        <p style="color: #003366; font-size: 18px; line-height: 1.5;">
            Ihre professionelle Drohnen-Dienstleistungs-App für den Hochbau.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.info("Starten Sie den 'SafeSite-Check' um Fotos oder Videos zu analysieren.")
    # Social Links ...
    col1, col2, col3 = st.columns(3)
    link_insta = "https://instagram.com/safesitedrohne" 
    link_face = "https://facebook.com/safesitedrohne"
    link_web = "https://safesitedrohne.ch"
    with col1: st.markdown(f'<a href="{link_insta}" target="_blank" class="social-link">📸 Instagram</a>', unsafe_allow_html=True)
    with col2: st.markdown(f'<a href="{link_face}" target="_blank" class="social-link">👍 Facebook</a>', unsafe_allow_html=True)
    with col3: st.markdown(f'<a href="{link_web}" target="_blank" class="social-link">🌍 Webseite</a>', unsafe_allow_html=True)

elif selected_mode == "🛡️ SafeSite-Check":
    
    if not st.session_state.logged_in:
        st.subheader("🔒 Geschützter Bereich")
        col_login, col_empty = st.columns([1, 2])
        with col_login:
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            if st.button("Einloggen", key="login_btn"):
                users = load_users() 
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.error("Falsche Daten.")
        
    else:
        # --- APP START ---
        if st.session_state.app_step == 'screen_a':
            st.subheader("Neuer Auftrag") 
            st.info("Laden Sie hier Ihre Drohnenaufnahmen hoch (Video ODER Fotos).")
            
            # WICHTIG: Erlaubt jetzt mehrere Dateien und Bilder!
            uploaded_files = st.file_uploader("Media Upload", type=["mp4", "jpg", "jpeg", "png"], accept_multiple_files=True)
            
            if uploaded_files:
                if st.button("Analyse starten"):
                    # Checken: Ist es Video oder Bild?
                    file_list = []
                    media_type = "images" # Standard-Annahme
                    
                    # Wir prüfen die erste Datei
                    first_file = uploaded_files[0]
                    if first_file.name.lower().endswith(".mp4"):
                        media_type = "video"
                        # Bei Video nehmen wir nur das erste (um Chaos zu vermeiden)
                        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                        tfile.write(first_file.read())
                        file_list.append(tfile.name)
                        tfile.close()
                    else:
                        # Bei Bildern speichern wir alle
                        for ufile in uploaded_files:
                            suffix = os.path.splitext(ufile.name)[1]
                            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                            tfile.write(ufile.read())
                            file_list.append(tfile.name)
                            tfile.close()
                    
                    st.session_state.media_type = media_type
                    st.session_state.media_files = file_list
                    st.session_state.app_step = 'screen_b'
                    st.rerun()

        elif st.session_state.app_step == 'screen_b':
            st.subheader("🔍 Scanner")
            
            media_type = st.session_state.media_type
            media_files = st.session_state.media_files
            
            # Anzeige der Medien
            if media_type == "video":
                st.video(media_files[0])
            else:
                # Galerie anzeigen
                st.write(f"📸 {len(media_files)} Fotos geladen")
                cols = st.columns(3)
                for i, img_path in enumerate(media_files):
                    with cols[i % 3]:
                        st.image(img_path, use_container_width=True, caption=f"Bild {i+1}")

            # KI Analyse
            if not st.session_state.analysis_data:
                status = st.status("🤖 KI analysiert Baustelle...", expanded=True)
                try:
                    if "HIER_EINFÜGEN" in API_KEY:
                        st.error("API Key fehlt!")
                    else:
                        genai.configure(api_key=API_KEY)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        if media_type == "video":
                            # VIDEO ANALYSE
                            status.write("Video Upload zu Google...")
                            video_file = genai.upload_file(media_files[0])
                            while video_file.state.name == "PROCESSING":
                                time.sleep(1)
                                video_file = genai.get_file(video_file.name)
                            
                            status.write("Suche Verstösse...")
                            prompt = """
                            Analysiere das Video nach BauAV/SUVA. Finde 3 Mängel.
                            JSON Format: [{"kategorie": "...", "prioritaet": "Hoch", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 10}]
                            """
                            response = model.generate_content([video_file, prompt], generation_config={"response_mime_type": "application/json"})
                            st.session_state.analysis_data = json.loads(clean_json_string(response.text))
                            
                        else:
                            # BILD ANALYSE (Neu!)
                            status.write("Analysiere Fotos...")
                            image_parts = []
                            for path in media_files:
                                img = Image.open(path)
                                image_parts.append(img)
                            
                            prompt = """
                            Du bist Schweizer Bau-Sicherheitsexperte (SiBe).
                            Analysiere diese Bilder nach BauAV/SUVA.
                            Finde Mängel auf den Bildern.
                            WICHTIG: Gib an, auf welchem Bild (Index 0 bis X) der Mangel ist.
                            
                            JSON Format: 
                            [{"kategorie": "...", "prioritaet": "Hoch", "mangel": "...", "verstoss": "...", "massnahme": "...", "bild_index": 0}]
                            """
                            # Wir senden Text + Alle Bilder
                            content_list = [prompt] + image_parts
                            response = model.generate_content(content_list, generation_config={"response_mime_type": "application/json"})
                            st.session_state.analysis_data = json.loads(clean_json_string(response.text))
                            
                        status.update(label="Fertig!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Fehler: {e}")
            
            # Ergebnisse anzeigen
            if st.session_state.analysis_data:
                st.markdown("### ⚠️ Ergebnisse prüfen")
                with st.form("validation_form"):
                    confirmed = []
                    for i, item in enumerate(st.session_state.analysis_data):
                        col_img, col_text = st.columns([1, 2])
                        with col_img:
                            # Bildanzeige Logik
                            if media_type == "video":
                                img = extract_frame(media_files[0], item.get('zeitstempel_sekunden', 0))
                                if img is not None: st.image(img, use_container_width=True)
                            else:
                                # Foto anzeigen
                                idx = item.get('bild_index', 0)
                                if idx < len(media_files):
                                    st.image(media_files[idx], use_container_width=True)
                                    
                        with col_text:
                            st.markdown(f"**{i+1}. {item.get('kategorie')}**")
                            st.write(f"🛑 {item.get('mangel')}")
                            st.caption(f"⚖️ {item.get('verstoss')}")
                            if st.checkbox(f"✅ Bestätigen", value=True, key=f"check_{i}"):
                                confirmed.append(item)
                        st.divider()
                    if st.form_submit_button("✅ Prüfung abschliessen & Bericht erstellen"):
                        st.session_state.confirmed_items = confirmed
                        st.session_state.app_step = 'screen_c'
                        st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("📄 Bericht")
            count = len(st.session_state.confirmed_items)
            
            if count > 0:
                # PDF Funktion aufrufen (angepasst für Bilder!)
                pdf_file = create_smart_pdf(st.session_state.confirmed_items, st.session_state.media_type, st.session_state.media_files)
                
                col1, col2 = st.columns(2)
                with col1:
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 PDF Speichern", f, "SSD_Bericht.pdf", "application/pdf", use_container_width=True)
                with col2:
                    subject = "Sicherheitsbericht SSD SafeSite"
                    body = f"Grüezi,\n\nanbei der Bericht.\n\nSSD Team"
                    mailto = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    st.link_button("📧 An Bauführer senden", mailto, use_container_width=True)
            else:
                st.success("Keine Mängel ausgewählt.")
                
            st.divider()
            if st.button("🏠 Neuer Flug"):
                # Reset
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.session_state.media_files = []
                st.session_state.media_type = None
                st.session_state.confirmed_items = []
                st.rerun()

# --- ADMIN / KUNDEN ---
elif st.session_state.logged_in and st.session_state.current_user == "admin" and selected_mode == "👥 Kundenverwaltung":
    st.subheader("👥 Kundenverwaltung")
    with st.expander("➕ Neuer Kunde"):
        with st.form("new_user"):
            nu = st.text_input("Name")
            np = st.text_input("Code")
            if st.form_submit_button("Speichern"):
                save_user(nu, np); st.rerun()
    st.json(load_users())

# --- BAUAV & REGELN (gekürzt für Übersicht, Funktion bleibt) ---
elif selected_mode == "📚 BauAV Nachschlagewerk":
    st.subheader("📚 BauAV")
    # ... (Dein BauAV Code hier, unverändert) ...
    st.info("Hier stehen deine BauAV Artikel.")

elif selected_mode == "📋 8 Lebenswichtige Regeln":
    st.subheader("🇨🇭 SUVA Regeln")
    # ... (Dein Regeln Code hier, unverändert) ...
    st.info("Hier stehen deine 8 Regeln.")
