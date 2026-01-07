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
import urllib.parse # Wichtig für den Email-Link

# Falls python-docx fehlt, fangen wir den Fehler ab
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

# DATEIEN
LOGO_FILE = "logo.jpg"
TITELBILD_FILE = "titelbild.png"

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
    try:
        img = Image.open(image_path)
        img_format = img.format or ''
        if img_format.upper() == 'MPO' or (img_format and img_format.upper() not in ['JPEG', 'PNG', 'WEBP', 'JPG']):
            if img.mode != 'RGB': img = img.convert('RGB')
            temp_path = image_path.replace('.mpo', '.jpg').replace('.MPO', '.jpg')
            if temp_path == image_path: temp_path = image_path + '_converted.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            return temp_path
        if img.mode != 'RGB':
            img = img.convert('RGB')
            temp_path = image_path.rsplit('.', 1)[0] + '_converted.jpg'
            img.save(temp_path, 'JPEG', quality=95)
            return temp_path
        return image_path
    except Exception as e:
        return image_path

# --- PDF GENERATOR (NEUES DESIGN: LOGO RECHTS) ---
class PDF(FPDF):
    def header(self):
        # Logo oben RECHTS platzieren (x=160, y=8)
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 160, 8, 40)
            except: pass
        self.ln(5)

def create_pdf(data, m_type, m_files, projekt, inspektor, status):
    pdf = PDF()
    pdf.add_page()
    
    # --- HEADER BEREICH (Wie Screenshot) ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SICHERHEITS-INSPEKTION (DROHNE)", ln=True)
    pdf.ln(8)
    
    # Metadaten Tabelle
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Projekt:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, projekt, ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Datum:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, date.today().strftime('%d.%m.%Y') + f" | {time.strftime('%H:%M')} Uhr", ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Inspektor:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"{inspektor} (SafeSite Drohne)", ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Status:", ln=0)
    pdf.set_font("Arial", '', 11)
    # Status Farbe (Orange bei Massnahmen)
    if "Massnahmen" in status: pdf.set_text_color(255, 153, 51)
    else: pdf.set_text_color(0, 153, 0)
    pdf.cell(0, 8, status, ln=True)
    pdf.set_text_color(0, 0, 0) # Reset
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. ZUSAMMENFASSUNG / MÄNGELLISTE", ln=True)
    pdf.ln(5)
    
    # --- INHALT ---
    for i, item in enumerate(data):
        if pdf.get_y() > 220: pdf.add_page()
        
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(204, 0, 0)
        titel = f"{i+1}. {item.get('kategorie', 'Mangel')} ({item.get('prioritaet', 'Mittel')})"
        pdf.cell(0, 8, titel.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
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
            
    # --- FOOTER / UNTERSCHRIFTEN ---
    if pdf.get_y() > 200: pdf.add_page()
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. FREIGABE", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Dieser Bericht wurde generiert durch SafeSite Drohne.", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Hinweis: Dieser Bericht dient als visuelle Unterstuetzung. Er entbindet die zustaendige Bauleitung nicht von der gesetzlichen Kontrollpflicht.")
    pdf.ln(20)
    
    # Linien
    pdf.set_font("Arial", 'B', 11); pdf.set_text_color(0,0,0)
    pdf.cell(40, 10, "Erstellt durch:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(80, 10, f"{inspektor} (SafeSite)", ln=0)
    pdf.cell(0, 10, "__________________________ (Datum/Unterschrift)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 10, "Verantwortlicher:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(80, 10, "Bauleitung / Polier", ln=0)
    pdf.cell(0, 10, "__________________________ (Datum/Unterschrift)", ln=True)

    out = "Bericht.pdf"
    pdf.output(out)
    return out

# --- WORD GENERATOR (NEUES DESIGN) ---
def create_word(data, m_type, m_files, projekt, inspektor, status):
    if not WORD_AVAILABLE: return None
    doc = Document()
    
    # Logo (Versuch rechtsbündig)
    if os.path.exists(LOGO_FILE):
        try:
            doc.add_picture(LOGO_FILE, width=Inches(1.5))
            doc.paragraphs[-1].alignment = 2 # Rechts
        except: pass

    # Header
    doc.add_heading('SICHERHEITS-INSPEKTION (DROHNE)', 0)
    p = doc.add_paragraph()
    p.add_run("Projekt: ").bold = True; p.add_run(f"{projekt}\n")
    p.add_run("Datum: ").bold = True; p.add_run(f"{date.today().strftime('%d.%m.%Y')}\n")
    p.add_run("Inspektor: ").bold = True; p.add_run(f"{inspektor}\n")
    p.add_run("Status: ").bold = True; p.add_run(f"{status}")

    doc.add_heading('1. ZUSAMMENFASSUNG / MÄNGEL', level=1)
    
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('kategorie', 'Mangel')}", level=2)
        p = doc.add_paragraph()
        p.add_run("Mangel: ").bold = True; p.add_run(f"{item.get('mangel')}\n")
        p.add_run("Verstoss: ").bold = True; p.add_run(f"{item.get('verstoss')}\n")
        p.add_run("Massnahme: ").bold = True; p.add_run(f"{item.get('massnahme')}")
        
        img_path = None
        temp_created = False
        if m_type == "video":
            frame = extract_frame(m_files[0], item.get('zeitstempel_sekunden', 0))
            if frame is not None:
                img_path = f"temp_word_{i}.jpg"; cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)); temp_created = True
        elif m_type == "images":
            idx = item.get('bild_index', 0)
            if idx < len(m_files): img_path = m_files[idx]
        
        if img_path:
            try: doc.add_picture(img_path, width=Inches(4.5))
            except: pass
            if temp_created and os.path.exists(img_path): os.remove(img_path)

    # Footer
    doc.add_page_break()
    doc.add_heading('4. FREIGABE', level=1)
    doc.add_paragraph("Dieser Bericht wurde generiert durch SafeSite Drohne.")
    p = doc.add_paragraph("Hinweis: Dient als visuelle Unterstützung.")
    p.italic = True
    doc.add_paragraph(f"\nErstellt durch: {inspektor} \t____________________")
    doc.add_paragraph(f"\nVerantwortlicher: \t\t\t____________________")

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

# SIDEBAR
with st.sidebar:
    st.title("SafeSite Drohne")
    page_options = ["🏠 Startseite", "🔍 SafeSite-Check", "📋 SUVA Regeln", "⚖️ BauAV"]
    
    # Mapping für Navigation
    p_map = {'home':0, 'safesite':1, 'suva':2, 'bauav':3}
    curr_idx = p_map.get(st.session_state.current_page, 0)
    
    page = st.radio("Bereich wählen:", page_options, index=curr_idx)
    
    if page == "🏠 Startseite": st.session_state.current_page = 'home'
    elif page == "🔍 SafeSite-Check": st.session_state.current_page = 'safesite'
    elif page == "📋 SUVA Regeln": st.session_state.current_page = 'suva'
    elif page == "⚖️ BauAV": st.session_state.current_page = 'bauav'
    
    if st.session_state.current_page == 'safesite' and st.session_state.logged_in:
        st.divider()
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.rerun()

# HAUPTBEREICH
if st.session_state.current_page == 'home':
    st.header("🏠 Willkommen bei SafeSite Drohne")
    st.write("Wählen Sie einen Bereich aus der Sidebar aus.")
    st.info("💡 Der SafeSite-Check Bereich erfordert eine Anmeldung.")

elif st.session_state.current_page == 'safesite':
    if not st.session_state.logged_in:
        st.header("🔍 SafeSite-Check - Login")
        u = st.text_input("User")
        p = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Falsch")
    else:
        # APP START
        if st.session_state.app_step == 'screen_a':
            st.subheader("Neuer Auftrag")
            mode = st.radio("Quelle:", ["📹 Video", "📸 Fotos"], horizontal=True)
            files = []
            
            if mode == "📹 Video":
                vf = st.file_uploader("Video (mp4)", type=["mp4"])
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
            st.subheader("🕵️‍♂️ KI-Analyse")
            
            if st.session_state.m_type == "video": st.video(st.session_state.m_files[0])
            else: 
                cols = st.columns(3)
                for i, f in enumerate(st.session_state.m_files):
                    with cols[i % 3]: st.image(f, caption=f"Bild {i+1}")

            if not st.session_state.analysis_data:
                with st.spinner("KI analysiert (Modell Gemini 3.0/Pro)..."):
                    try:
                        genai.configure(api_key=API_KEY)
                        prompt = """
                        Du bist ein strenger Schweizer Bau-Sicherheitsprüfer (SiBe).
                        Analysiere diese Aufnahmen KRITISCH nach BauAV und SUVA.
                        WICHTIG - Suche gezielt nach LEBENSGEFAHR:
                        1. GRÄBEN: Steht ein Bagger im Graben? Sind Wände senkrecht (>1.5m) ohne Spriessung? (BauAV Art 19/20)
                        2. ARMIERUNG: Ragen Eisen heraus ohne Schutzkappen?
                        3. ABSTURZ: Fehlen Geländer?
                        Antworte NUR als JSON Liste:
                        [{"kategorie": "...", "prioritaet": "Kritisch/Hoch/Mittel", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                        """
                        model_names = ['gemini-3-pro-preview', 'gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-pro']
                        res = None
                        for mn in model_names:
                            try:
                                model = genai.GenerativeModel(mn)
                                if st.session_state.m_type == "video":
                                    f = genai.upload_file(st.session_state.m_files[0])
                                    while f.state.name == "PROCESSING": time.sleep(1)
                                    res = model.generate_content([f, prompt], generation_config={"response_mime_type": "application/json"})
                                else:
                                    imgs = [Image.open(p) for p in st.session_state.m_files] # Einfach
                                    res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                                break 
                            except: continue
                        
                        if res: st.session_state.analysis_data = json.loads(clean_json(res.text)); st.rerun()
                        else: st.error("Kein Modell verfügbar.")
                    except Exception as e: st.error(f"Fehler: {e}")

            if st.session_state.analysis_data:
                st.success(f"⚠️ {len(st.session_state.analysis_data)} Mängel gefunden")
                
                # --- HIER SIND DIE NEUEN EINGABEFELDER ---
                st.divider()
                st.markdown("### 📝 Projektdaten für Bericht")
                c_a, c_b = st.columns(2)
                with c_a:
                    proj = st.text_input("Projektname", value="Überbauung 'Luegisland', Wohlen AG")
                    insp = st.text_input("Inspektor Name", value="Dominik Marti")
                with c_b:
                    stat = st.selectbox("Status", ["⚠️ Massnahmen erforderlich", "✅ In Ordnung", "🛑 Kritisch - Baustopp"])
                st.divider()
                # -----------------------------------------

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
                            st.markdown(f":orange[**{item.get('prioritaet')}: {item.get('mangel')}**]")
                            st.write(item.get('massnahme'))
                            if st.checkbox("Aufnehmen", True, key=str(i)): confirmed.append(item)
                        st.divider()
                    
                    if st.form_submit_button("Berichte erstellen"):
                        st.session_state.confirmed = confirmed
                        # Daten Speichern
                        st.session_state.meta_p = proj
                        st.session_state.meta_i = insp
                        st.session_state.meta_s = stat
                        st.session_state.app_step = 'screen_c'
                        st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("Berichte fertig!")
            
            # Daten holen
            p = st.session_state.get('meta_p', '')
            i = st.session_state.get('meta_i', '')
            s = st.session_state.get('meta_s', '')

            pdf_file = create_pdf(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files, p, i, s)
            
            c1, c2 = st.columns(2)
            with c1:
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 PDF Bericht", f, "SSD_Bericht.pdf", mime="application/pdf", use_container_width=True)
            with c2:
                if WORD_AVAILABLE:
                    word_file = create_word(st.session_state.confirmed, st.session_state.m_type, st.session_state.m_files, p, i, s)
                    with open(word_file, "rb") as f:
                        st.download_button("📝 Word Bericht", f, "SSD_Bericht.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

            # --- EMAIL BUTTON ---
            st.divider()
            st.markdown("### 📧 Versenden")
            email_to = st.text_input("Empfänger Email", placeholder="kunde@bau.ch")
            
            if email_to:
                subject = f"Sicherheitsbericht: {p}"
                body = f"Grüezi,\n\nanbei erhalten Sie den Sicherheitsbericht für das Projekt {p}.\n\nInspektor: {i}\nStatus: {s}\n\nFreundliche Grüsse\nSafeSite Drohne"
                safe_s = urllib.parse.quote(subject)
                safe_b = urllib.parse.quote(body)
                mailto = f"mailto:{email_to}?subject={safe_s}&body={safe_b}"
                
                st.link_button("📧 Email-Entwurf öffnen (PDF bitte anhängen)", mailto)
            else:
                st.caption("Geben Sie eine Email-Adresse ein, um den Senden-Button zu sehen.")

            if st.button("Neuer Auftrag"):
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.rerun()

elif st.session_state.current_page == 'suva':
    st.header("📋 SUVA Regeln")
    for i in range(1, 9):
        f = f"regel_{i}.png"
        if os.path.exists(f): st.image(f)

elif st.session_state.current_page == 'bauav':
    st.header("⚖️ BauAV")
    # BauAV Inhalt hier...
