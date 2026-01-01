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

# ==========================================
# 0. SETUP & KONFIGURATION
# ==========================================
st.set_page_config(page_title="SafeSite Drohne", page_icon="logo.jpg", layout="wide")
# ----------------------------------------------------

# 🔒 DATEI FÜR BENUTZERDATEN
USER_DB_FILE = "users.json"

# Funktion: Benutzer laden
def load_users():
    if not os.path.exists(USER_DB_FILE):
        default_users = {"admin": "SafeSite"} 
        with open(USER_DB_FILE, "w") as f:
            json.dump(default_users, f)
        return default_users
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

# Funktion: Benutzer speichern (Neu oder Ändern)
def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

# Funktion: Benutzer LÖSCHEN (Neu!)
def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f)

# 🔴 API Key sicher aus den Secrets laden (für Cloud)
try:
    # Versuch 1: Wir sind in der Cloud (Secrets Tresor)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Versuch 2: Wir sind lokal auf dem MacBook (Notfall-Lösung)
    # Hier deinen Schlüssel für lokale Tests einfügen, falls nötig
    API_KEY = "AIzaSyC6VlkfBdItsTWec69GXN2dExTQjlT9LgQ"

# Setup
try:
    genai.configure(api_key=API_KEY)
except:
    pass

LOGO_FILE = "logo.jpg" 
TITELBILD_FILE = "titelbild.png" 

# --- DESIGN & CSS ---
st.markdown("""
<style>
    /* Hauptfarben */
    :root {
        --primary: #FF6600;
        --dark: #333333;
    }
    
    /* Grosse Buttons */
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

    /* Überschriften allgemein */
    h1, h2, h3, h4 {
        font-family: 'Arial', sans-serif;
    }
    
    /* Social Media Links auf Home */
    .social-link {
        display: inline-block;
        padding: 10px 20px;
        margin: 10px;
        color: white !important;
        background-color: #333;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        width: 100%;
    }
    .social-link:hover {
        background-color: #FF6600;
    }
    
    /* Login Box Styling */
    .login-box {
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        border-top: 5px solid #FF6600;
        margin-bottom: 20px;
    }
    
    /* Checkbox gross machen */
    .stCheckbox {
        transform: scale(1.3);
        margin-top: 10px;
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
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'confirmed_items' not in st.session_state:
    st.session_state.confirmed_items = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# ==========================================
# 2. HILFS-FUNKTIONEN (PDF & BILD)
# ==========================================

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 10, 8, 40)
            except: pass
        self.set_font('Arial', 'B', 16)
        self.set_xy(60, 15)
        self.set_text_color(255, 102, 0) # Orange
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
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except: return None
    return None

def create_smart_pdf(data_list, video_path):
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

        img = extract_frame(video_path, item.get('zeitstempel_sekunden', 0))
        if img is not None:
            temp = f"temp_{idx}.jpg"
            cv2.imwrite(temp, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            pdf.image(temp, x=20, w=140)
            pdf.ln(5)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 5, f"Abb: Szene bei Sekunde {item.get('zeitstempel_sekunden', 0)}", ln=True, align='C')
            pdf.ln(10)
            if os.path.exists(temp): os.remove(temp)
        else:
            pdf.ln(5)

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
# 3. SIDEBAR NAVIGATION & LOGOUT
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
            st.session_state.confirmed_items = []
            st.session_state.video_path = None
            st.rerun()
            
    st.caption("SSD SafeSite App v12.0")

# ==========================================
# HAUPTBEREICH: TITELBILD
# ==========================================
if os.path.exists(TITELBILD_FILE):
    st.image(TITELBILD_FILE, use_container_width=True)

st.markdown("<h1 style='text-align: center; color: #FF6600; font-size: 40px; margin-bottom: 30px;'>SafeSite Drohne</h1>", unsafe_allow_html=True)

# ==========================================
# LOGIK VERTEILER
# ==========================================

# >>> MODUS 0: HOME <<<
if selected_mode == "🏠 Home":
    st.markdown("""
    <div style="background-color: #E0E0E0; padding: 20px; border-radius: 10px; border-left: 5px solid #FF6600; margin-bottom: 30px;">
        <h2 style="color: #FF6600; margin-top: 0;">Willkommen bei SafeSite Drohne</h2>
        <p style="color: #003366; font-size: 18px; line-height: 1.5;">
            Ihre professionelle Drohnen-Dienstleistungs-App für den Hochbau.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Wählen Sie im Menü links 'SafeSite-Check' um einen neuen Drohnenflug zu analysieren.")
    
    st.write("---")
    st.markdown("### 🌐 Social Media & Web")
    
    col1, col2, col3 = st.columns(3)
    
    link_insta = "https://instagram.com/safesitedrohne" 
    link_face = "https://www.facebook.com/profile.php?id=61585259470058"
    link_web = "https://safesitedrohne.ch"
    
    with col1:
        st.markdown(f'<a href="{link_insta}" target="_blank" class="social-link">📸 Instagram</a>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<a href="{link_face}" target="_blank" class="social-link">👍 Facebook</a>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<a href="{link_web}" target="_blank" class="social-link">🌍 Webseite</a>', unsafe_allow_html=True)


# >>> MODUS 2: DER DROHNEN CHECK (GESCHÜTZT) <<<
elif selected_mode == "🛡️ SafeSite-Check":
    
    if not st.session_state.logged_in:
        st.subheader("🔒 Geschützter Bereich")
        
        st.markdown("""
        <div style="background-color: #E0E0E0; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #FF6600;">
            <h4 style="color: #FF6600; margin-top: 0;">Login erforderlich</h4>
            <div style="color: #003366; font-size: 16px; line-height: 1.5;">
                Bitte melden Sie sich an, um den Sicherheits-Check zu nutzen.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_login, col_empty = st.columns([1, 2])
        with col_login:
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            
            if st.button("Einloggen", key="login_btn"):
                users = load_users() 
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success("Erfolgreich eingeloggt!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Benutzername oder Passwort falsch.")
        
        st.divider()
        st.info("Noch keinen Zugang? Kontaktieren Sie SSD SafeSite Drohne für ein Angebot.")
        
    else:
        # APP ABLAUF
        if st.session_state.app_step == 'screen_a':
            st.subheader("SafeSite-Check") 
            st.info(f"Bereit für einen neuen Auftrag, {st.session_state.current_user}?")
            uploaded_file = st.file_uploader("Start: Video hochladen oder Kamera öffnen", type=["mp4"])
            if uploaded_file:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(uploaded_file.read())
                st.session_state.video_path = tfile.name
                tfile.close()
                st.session_state.app_step = 'screen_b'
                st.rerun()

        elif st.session_state.app_step == 'screen_b':
            st.subheader("🔍 Scanner")
            video_path = st.session_state.video_path
            st.video(video_path)
            
            if not st.session_state.analysis_data:
                status = st.status("🤖 KI analysiert Video...", expanded=True)
                try:
                    if "HIER_EINFÜGEN" in API_KEY:
                        st.error("API Key fehlt!")
                    else:
                        status.write("Upload zu Google...")
                        genai.configure(api_key=API_KEY)
                        video_file = genai.upload_file(video_path)
                        while video_file.state.name == "PROCESSING":
                            time.sleep(1)
                            video_file = genai.get_file(video_file.name)
                        
                        status.write("Suche Verstösse gegen BauAV...")
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        prompt = """
                        Du bist ein Schweizer Bau-Sicherheitsexperte (SiBe).
                        Analysiere das Video STRENG nach **Bauarbeitenverordnung (BauAV)** und SUVA-Regeln.
                        Finde 3 Mängel.
                        Gib das Ergebnis NUR als JSON-Liste zurück.
                        Format:
                        [{"kategorie": "...", "prioritaet": "Hoch", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 10}]
                        WICHTIG: Nenne im Feld 'verstoss' IMMER den konkreten Artikel (z.B. BauAV Art. X).
                        """
                        response = model.generate_content([video_file, prompt], generation_config={"response_mime_type": "application/json"})
                        st.session_state.analysis_data = json.loads(clean_json_string(response.text))
                        status.update(label="Fertig!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Fehler: {e}")
            
            if st.session_state.analysis_data:
                st.markdown("### ⚠️ Ergebnisse prüfen")
                with st.form("validation_form"):
                    confirmed = []
                    for i, item in enumerate(st.session_state.analysis_data):
                        col_img, col_text = st.columns([1, 2])
                        with col_img:
                            img = extract_frame(video_path, item.get('zeitstempel_sekunden', 0))
                            if img is not None: st.image(img, use_container_width=True)
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
            if count == 0: st.success("Keine Mängel!")
            else: st.warning(f"⚠️ {count} Mängel dokumentiert.")
            if count > 0:
                pdf_file = create_smart_pdf(st.session_state.confirmed_items, st.session_state.video_path)
                col1, col2 = st.columns(2)
                with col1:
                    with open(pdf_file, "rb") as f:
                        st.download_button("📥 PDF Speichern", f, "SSD_Bericht.pdf", "application/pdf", use_container_width=True)
                with col2:
                    subject = "Sicherheitsbericht SSD SafeSite"
                    body = f"Grüezi,\n\nanbei der Bericht mit {count} Mängeln gemäss BauAV.\n\nSSD Team"
                    mailto = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    st.link_button("📧 PDF an Bauführer senden", mailto, use_container_width=True)
            st.divider()
            if st.button("🏠 Neuer Flug"):
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.session_state.confirmed_items = []
                st.session_state.video_path = None
                st.rerun()

# >>> MODUS 4: ADMIN / KUNDENVERWALTUNG (UPDATE) <<<
elif st.session_state.logged_in and st.session_state.current_user == "admin" and selected_mode == "👥 Kundenverwaltung":
    st.subheader("👥 Kundenverwaltung (Admin)")
    st.markdown("Hier können Sie Kunden verwalten.")
    
    # 1. NEUEN KUNDEN ANLEGEN
    with st.expander("➕ Neuen Kunden anlegen", expanded=True):
        with st.form("new_user_form"):
            new_user = st.text_input("Firmenname / Benutzername")
            new_pass = st.text_input("Zugangscode (Passwort)")
            if st.form_submit_button("Speichern"):
                if new_user and new_pass:
                    save_user(new_user, new_pass)
                    st.success(f"Kunde '{new_user}' angelegt!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Bitte Namen und Code eingeben.")

    # 2. KUNDEN LÖSCHEN
    st.divider()
    with st.expander("🗑️ Kunde löschen"):
        users = load_users()
        # Admin darf sich nicht selbst löschen
        user_list = [u for u in users.keys() if u != "admin"]
        
        if user_list:
            user_to_delete = st.selectbox("Benutzer auswählen zum Löschen", user_list)
            if st.button(f"Benutzer '{user_to_delete}' unwiderruflich löschen"):
                delete_user(user_to_delete)
                st.success(f"Benutzer '{user_to_delete}' gelöscht.")
                time.sleep(0.5)
                st.rerun()
        else:
            st.info("Keine löschbaren Benutzer vorhanden.")

    st.divider()
    st.write("Aktive Benutzer in Datenbank:")
    st.json(load_users())

# >>> MODUS 3: BAUAV NACHSCHLAGEWERK <<<
elif selected_mode == "📚 BauAV Nachschlagewerk":
    st.subheader("📚 Wichtige BauAV Artikel")
    st.markdown("Auszug aus der Verordnung über die Sicherheit bei Bauarbeiten (SR 832.311.141).")
    st.write("") 

    def bauav_card(titel, art, inhalt):
        html_code = f"""
<div style="background-color: #E0E0E0; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #FF6600;">
    <h3 style="color: #FF6600; margin-top: 0;">{titel} <span style="font-size: 0.8em; color: #666;">({art})</span></h3>
    <div style="color: #003366; font-size: 16px; line-height: 1.5;">
        {inhalt}
    </div>
</div>
"""
        st.markdown(html_code, unsafe_allow_html=True)

    bauav_card("Absturzsicherung", "BauAV Art. 18 ff.", "<b>Grundsatz:</b> Massnahmen sind ab einer Absturzhöhe von <b>2.00 m</b> zwingend erforderlich.<br><b>Seitenschutz:</b> Besteht aus Geländerholm (100cm), Zwischenholm und Bordbrett (15cm).<br><b>Bodenöffnungen:</b> Müssen durchbruchsicher und unverrückbar abgedeckt sein.")
    bauav_card("Gräben & Baugruben", "BauAV Art. 68 ff.", "<b>Sicherungspflicht:</b> Ab einer Tiefe von <b>1.50 m</b> müssen Wände geböscht oder verspriesst werden.<br><b>Breite:</b> Arbeitsraum muss mind. 60 cm breit sein.<br><b>Zugänge:</b> Leitern/Treppen in Gräben müssen alle 5m einen Austritt ermöglichen.")
    bauav_card("Arbeitsgerüste", "BauAV Art. 47 ff.", "<b>Kontrolle:</b> Tägliche Sichtkontrolle durch den Benutzer ist Pflicht.<br><b>Beläge:</b> Dicht verlegt, keine Spalten > 2.5cm, gegen Wippen gesichert.<br><b>Fassadengerüst:</b> Zwingend ab 3.00 m Absturzhöhe.")
    bauav_card("Persönliche Schutzausrüstung", "BauAV Art. 6 & 7", "<b>Helm:</b> Tragpflicht bei Hochbauarbeiten bis Rohbauende und bei Kranarbeiten.<br><b>Warnkleidung:</b> Zwingend bei Arbeiten im Bereich von Baumaschinen oder Strassenverkehr.")
    bauav_card("Leitern", "BauAV Art. 20 ff.", "<b>Sicherung:</b> Gegen Wegrutschen und Kippen sichern.<br><b>Überstand:</b> Muss beim Austritt mind. 1.00 m überragen.<br><b>Einsatz:</b> Nur für kurzzeitige Arbeiten oder wenn Gerüste technisch nicht möglich sind.")

# >>> MODUS 1: DIE 8 REGELN <<<
elif selected_mode == "📋 8 Lebenswichtige Regeln":
    st.subheader("🇨🇭 Die 8 lebenswichtigen Regeln")
    st.markdown("Basis: Suva Publikation 84035.d")
    st.divider()

    regeln = [
        {"nr": 1, "titel": "Absturzkanten sichern", "text": "Wir sichern Absturzkanten ab einer Absturzhöhe von 2 m.", "img": "regel_1.png"},
        {"nr": 2, "titel": "Bodenöffnungen verschliessen", "text": "Wir sichern Bodenöffnungen sofort durchbruchsicher und unverrückbar.", "img": "regel_2.png"},
        {"nr": 3, "titel": "Lasten richtig anschlagen", "text": "Wir bedienen Krane vorschriftsgemäss und schlagen Lasten sicher an.", "img": "regel_3.png"},
        {"nr": 4, "titel": "Mit Fassadengerüst arbeiten", "text": "Wir arbeiten ab einer Absturzhöhe von 3 m nur mit Fassadengerüst.", "img": "regel_4.png"},
        {"nr": 5, "titel": "Täglich Gerüstkontrollen", "text": "Wir kontrollieren die Gerüste täglich. Ich benutze nur sichere Gerüste.", "img": "regel_5.png"},
        {"nr": 6, "titel": "Sichere Zugänge", "text": "Wir erstellen sichere Zugänge zu allen Arbeitsplätzen.", "img": "regel_6.png"},
        {"nr": 7, "titel": "Persönliche Schutzausrüstung", "text": "Wir tragen die persönliche Schutzausrüstung (Helm, Schuhe, etc.).", "img": "regel_7.png"},
        {"nr": 8, "titel": "Gräben und Baugruben sichern", "text": "Wir sichern Gräben und Baugruben ab einer Tiefe von 1,5 m.", "img": "regel_8.png"},
    ]

    for regel in regeln:
        with st.container(border=True):
            col_img, col_txt = st.columns([1, 2])
            with col_img:
                if os.path.exists(regel["img"]): st.image(regel["img"], use_container_width=True)
                else: st.warning(f"Bild fehlt: {regel['img']}")
            with col_txt:
                st.subheader(f"Regel {regel['nr']}: {regel['titel']}")
                st.write(regel["text"])
