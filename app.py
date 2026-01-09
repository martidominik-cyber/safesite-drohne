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
import urllib.parse
import uuid 

# Word-Modul sicher laden
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
    h1, h2, h3 {{ color: #FF6600 !important; }}
</style>
<link rel="apple-touch-icon" href="{LOGO_URL_GITHUB}">
""", unsafe_allow_html=True)

# DATENBANK
USER_DB_FILE = "users.json"
CUSTOMERS_DB_FILE = "customers.json"

def load_users():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f: json.dump({"admin": "1234"}, f)
    with open(USER_DB_FILE, "r") as f: return json.load(f)

def save_users(users):
    with open(USER_DB_FILE, "w") as f: json.dump(users, f, indent=2)

def load_customers():
    if not os.path.exists(CUSTOMERS_DB_FILE):
        with open(CUSTOMERS_DB_FILE, "w") as f: json.dump({}, f)
    with open(CUSTOMERS_DB_FILE, "r") as f: return json.load(f)

def save_customers(customers):
    with open(CUSTOMERS_DB_FILE, "w") as f: json.dump(customers, f, indent=2)

def is_admin():
    return st.session_state.logged_in and st.session_state.username == "admin"

def get_customer_by_email(email):
    """Findet einen Kunden anhand seiner Email-Adresse"""
    customers = load_customers()
    for kunde_id, kunde_data in customers.items():
        if kunde_data.get('email') == email:
            return kunde_id, kunde_data
    return None, None

def get_customer_credits(email):
    """Gibt die Credits eines Kunden zurück (0 falls nicht gefunden)"""
    kunde_id, kunde_data = get_customer_by_email(email)
    if kunde_data:
        return int(kunde_data.get('credits', 0))
    return 0

def deduct_credit(email):
    """Zieht 1 Credit vom Kunden ab und speichert"""
    customers = load_customers()
    kunde_id, kunde_data = get_customer_by_email(email)
    if kunde_id and kunde_data:
        current_credits = int(kunde_data.get('credits', 0))
        if current_credits > 0:
            customers[kunde_id]['credits'] = current_credits - 1
            save_customers(customers)
            return True
    return False

def update_customer_credits(kunde_id, credits):
    """Aktualisiert die Credits eines Kunden"""
    customers = load_customers()
    if kunde_id in customers:
        customers[kunde_id]['credits'] = int(credits)
        save_customers(customers)
        return True
    return False

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

def convert_image_if_needed(img_path):
    """Konvertiert Bilder in ein Format, das von PIL verarbeitet werden kann"""
    try:
        # Prüfe ob es eine HEIC/HEIF Datei ist
        if img_path.lower().endswith(('.heic', '.heif')):
            # Versuche zuerst mit PIL (falls pillow-heif installiert ist)
            try:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                new_path = img_path.rsplit('.', 1)[0] + '.jpg'
                img.save(new_path, 'JPEG', quality=95)
                # Alte Datei löschen
                if os.path.exists(img_path):
                    try: os.remove(img_path)
                    except: pass
                return new_path
            except:
                # PIL kann HEIC nicht öffnen, versuche mit OpenCV
                pass
            
            # Versuche mit OpenCV (kann manchmal HEIC lesen, wenn entsprechende Codecs vorhanden sind)
            try:
                img_array = cv2.imread(img_path, cv2.IMREAD_COLOR)
                if img_array is not None and img_array.size > 0:
                    new_path = img_path.rsplit('.', 1)[0] + '.jpg'
                    cv2.imwrite(new_path, img_array, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    if os.path.exists(img_path):
                        try: os.remove(img_path)
                        except: pass
                    return new_path
            except:
                pass
            
            # Falls beides fehlschlägt, gib Warnung aus aber behalte Originaldatei
            # (möglicherweise unterstützt der Browser die Konvertierung beim Upload)
            return img_path
        
        # Für andere Formate, versuche einfach zu öffnen
        try:
            img = Image.open(img_path)
            # Stelle sicher, dass es RGB ist
            if img.mode != 'RGB' and img.mode not in ['RGBA', 'P']:
                # Konvertiere problematische Formate
                if img.mode in ['RGBA', 'P']:
                    # Erstelle weissen Hintergrund für transparente Bilder
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        rgb_img.paste(img, mask=img.split()[3])
                    else:
                        rgb_img.paste(img)
                    new_path = img_path.rsplit('.', 1)[0] + '_rgb.jpg'
                    rgb_img.save(new_path, 'JPEG', quality=95)
                    if img_path != new_path and os.path.exists(img_path):
                        try: os.remove(img_path)
                        except: pass
                    return new_path
            return img_path
        except:
            return img_path
            
    except Exception as e:
        # Bei jedem Fehler, gib die Originaldatei zurück
        return img_path

# --- PDF GENERATOR ---
class PDF(FPDF):
    def header(self):
        # Logo oben RECHTS platzieren
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 160, 8, 40)
            except: pass
        self.ln(5)

def make_safe_text(text):
    """Entfernt Emojis für das PDF, damit es nicht abstürzt"""
    if text is None: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_pdf(data, m_type, m_files, projekt, inspektor, status):
    pdf = PDF()
    pdf.add_page()
    
    # --- HEADER BEREICH ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SICHERHEITS-INSPEKTION (DROHNE)", ln=True)
    pdf.ln(8)
    
    # Metadaten
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Projekt:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, make_safe_text(projekt), ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Datum:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, date.today().strftime('%d.%m.%Y') + f" | {time.strftime('%H:%M')} Uhr", ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Inspektor:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, make_safe_text(f"{inspektor} (SafeSite Drohne)"), ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(35, 8, "Status:", ln=0)
    pdf.set_font("Arial", '', 11)
    
    if "Massnahmen" in status: pdf.set_text_color(255, 153, 51)
    else: pdf.set_text_color(0, 153, 0)
    pdf.cell(0, 8, make_safe_text(status), ln=True)
    pdf.set_text_color(0, 0, 0) 
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. ZUSAMMENFASSUNG / MAENGELLISTE", ln=True)
    pdf.ln(5)
    
    # --- INHALT ---
    for i, item in enumerate(data):
        if pdf.get_y() > 220: pdf.add_page()
        
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(204, 0, 0)
        kat = make_safe_text(item.get('kategorie', 'Mangel'))
        prio = make_safe_text(item.get('prioritaet', 'Mittel'))
        titel = f"{i+1}. {kat} ({prio})"
        pdf.cell(0, 8, titel, ln=True)
        
        pdf.set_font("Arial", '', 10); pdf.set_text_color(0,0,0)
        pdf.multi_cell(0, 5, f"Mangel: {make_safe_text(item.get('mangel', '-'))}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Verstoss: {make_safe_text(item.get('verstoss', '-'))}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Massnahme: {make_safe_text(item.get('massnahme', '-'))}")
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
            
    # --- FOOTER ---
    if pdf.get_y() > 200: pdf.add_page()
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. FREIGABE", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, "Dieser Bericht wurde generiert durch SafeSite Drohne.", ln=True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Hinweis: Dieser Bericht dient als visuelle Unterstuetzung. Er entbindet die zustaendige Bauleitung nicht von der gesetzlichen Kontrollpflicht.")
    pdf.ln(20)
    
    # Angepasste Breiten
    w_label = 40
    w_name = 65 
    
    pdf.set_font("Arial", 'B', 11); pdf.set_text_color(0,0,0)
    pdf.cell(w_label, 10, "Erstellt durch:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(w_name, 10, make_safe_text(f"{inspektor}"), ln=0)
    pdf.cell(0, 10, "_______________________ (Datum/Unterschrift)", ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(w_label, 10, "Verantwortlicher:", ln=0)
    pdf.set_font("Arial", '', 11)
    pdf.cell(w_name, 10, "Bauleitung / Polier", ln=0)
    pdf.cell(0, 10, "_______________________ (Datum/Unterschrift)", ln=True, align='R')

    out = "Bericht.pdf"
    pdf.output(out)
    return out

# --- WORD GENERATOR ---
def create_word(data, m_type, m_files, projekt, inspektor, status):
    if not WORD_AVAILABLE: return None
    doc = Document()
    
    if os.path.exists(LOGO_FILE):
        try:
            doc.add_picture(LOGO_FILE, width=Inches(1.5))
            doc.paragraphs[-1].alignment = 2 
        except: pass

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
if 'username' not in st.session_state: st.session_state.username = None

# SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
        
    st.title("Menü")
    page_options = ["🏠 Startseite", "🔍 SafeSite-Check", "📋 SUVA Regeln", "⚖️ BauAV"]
    p_map = {'home':0, 'safesite':1, 'suva':2, 'bauav':3, 'kunden':4}
    
    # Admin-Menüpunkt hinzufügen, wenn Admin eingeloggt
    if is_admin():
        page_options.append("👥 Kundenverwaltung")
        p_map['kunden'] = len(page_options) - 1
    
    curr_idx = p_map.get(st.session_state.current_page, 0)
    # Sicherstellen, dass der Index nicht außerhalb des Bereichs liegt
    if curr_idx >= len(page_options):
        curr_idx = 0
        st.session_state.current_page = 'home'
    
    page = st.radio("Bereich wählen:", page_options, index=curr_idx)
    
    if page == "🏠 Startseite": st.session_state.current_page = 'home'
    elif page == "🔍 SafeSite-Check": st.session_state.current_page = 'safesite'
    elif page == "📋 SUVA Regeln": st.session_state.current_page = 'suva'
    elif page == "⚖️ BauAV": st.session_state.current_page = 'bauav'
    elif page == "👥 Kundenverwaltung": st.session_state.current_page = 'kunden'
    
    if st.session_state.logged_in:
        st.divider()
        st.info(f"✅ Eingeloggt als: **{st.session_state.username}**")
        
        # Credits-Anzeige nur für Kunden (nicht Admin)
        if not is_admin() and st.session_state.username:
            credits = get_customer_credits(st.session_state.username)
            st.metric("🪙 SafeSite Credits", credits)
        
        if st.button("Logout"): 
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.current_page = 'home'
            st.rerun()

# HAUPTBEREICH
if st.session_state.current_page == 'home':
    if os.path.exists(TITELBILD_FILE):
        st.image(TITELBILD_FILE, use_container_width=True)
    st.header("🏠 Willkommen bei SafeSite Drohne")
    st.write("Wählen Sie einen Bereich aus der Sidebar aus.")
    st.info("💡 Der SafeSite-Check Bereich erfordert eine Anmeldung.")

elif st.session_state.current_page == 'safesite':
    if not st.session_state.logged_in:
        st.header("🔍 SafeSite-Check - Login")
        st.info("💡 **Admin:** Verwenden Sie 'admin' als Username. **Kunden:** Verwenden Sie Ihre Email-Adresse als Username.")
        u = st.text_input("Username", placeholder="admin oder Email-Adresse")
        p = st.text_input("Passwort", type="password")
        if st.button("Einloggen"):
            users = load_users()
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Falsch")
    else:
        # APP START
        if st.session_state.app_step == 'screen_a':
            st.subheader("Neuer Auftrag")
            mode = st.radio("Quelle:", ["📹 Video", "📸 Fotos"], horizontal=True)
            files = []
            
            if mode == "📹 Video":
                st.info("💡 **Tipp:** Sie können Videos aus Ihrer Mediathek/Galerie auswählen (funktioniert auf Handy, Tablet und Laptop).")
                vf = st.file_uploader("Video hochladen", type=["mp4", "mov", "avi"], help="Unterstützte Formate: MP4, MOV, AVI")
                if vf:
                    st.success(f"✅ Video ausgewählt: {vf.name}")
                    if st.button("Analyse starten", type="primary", use_container_width=True):
                        suffix = os.path.splitext(vf.name)[1] if os.path.splitext(vf.name)[1] else '.mp4'
                        t = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                        t.write(vf.read())
                        files.append(t.name)
                        t.close()
                        st.session_state.m_type = "video"
                        st.session_state.m_files = files
                        st.session_state.app_step = 'screen_b'
                        st.rerun()
            else:
                st.info("💡 **Tipp:** Sie können Fotos aus Ihrer Galerie/Mediathek auswählen (funktioniert auf Handy, Tablet und Laptop).")
                pf = st.file_uploader(
                    "Fotos hochladen", 
                    type=["jpg", "jpeg", "png", "heic", "heif", "webp"], 
                    accept_multiple_files=True,
                    help="Wählen Sie ein oder mehrere Fotos aus. Unterstützt: JPG, PNG, HEIC (iPhone), WEBP"
                )
                if pf:
                    st.success(f"✅ {len(pf)} Foto(s) ausgewählt")
                    # Zeige Dateinamen an
                    for idx, f in enumerate(pf[:5]):  # Zeige max. 5 Dateien
                        st.caption(f"📷 {f.name}")
                    if len(pf) > 5:
                        st.caption(f"... und {len(pf) - 5} weitere")
                    
                    if st.button("Analyse starten", type="primary", use_container_width=True):
                        with st.spinner("Bilder werden verarbeitet..."):
                            for f in pf:
                                # Original-Dateiendung beibehalten
                                original_ext = os.path.splitext(f.name)[1].lower() if os.path.splitext(f.name)[1] else ''
                                # Verwende passende Endung basierend auf Dateityp
                                if original_ext in ['.heic', '.heif']:
                                    suffix = '.heic'  # Wird später konvertiert
                                elif original_ext in ['.jpg', '.jpeg']:
                                    suffix = '.jpg'
                                elif original_ext == '.png':
                                    suffix = '.png'
                                elif original_ext == '.webp':
                                    suffix = '.webp'
                                else:
                                    suffix = '.jpg'  # Standard
                                
                                t = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                                t.write(f.read())
                                files.append(t.name)
                                t.close()
                            
                            # Konvertiere HEIC/HEIF Dateien falls nötig
                            converted_files = []
                            for f_path in files:
                                converted_path = convert_image_if_needed(f_path)
                                converted_files.append(converted_path)
                            
                            st.session_state.m_type = "images"
                            st.session_state.m_files = converted_files
                            st.session_state.app_step = 'screen_b'
                            st.rerun()

        elif st.session_state.app_step == 'screen_b':
            st.subheader("🕵️‍♂️ KI-Analyse (Gemini 3.0)")
            if st.session_state.m_type == "video": st.video(st.session_state.m_files[0])
            else: 
                cols = st.columns(3)
                for i, f in enumerate(st.session_state.m_files):
                    with cols[i % 3]: st.image(f, caption=f"Bild {i+1}")

            if not st.session_state.analysis_data:
                with st.spinner("KI analysiert (Versuche Gemini 3.0... bitte warten)..."):
                    try:
                        genai.configure(api_key=API_KEY)
                        prompt = """
                        Du bist ein strenger Schweizer Bau-Sicherheitsprüfer (SiBe).
                        Analysiere diese Aufnahmen KRITISCH nach BauAV und SUVA.
                        Suche nach LEBENSGEFAHR (Gräben, Absturz, Armierung).
                        Antworte NUR als JSON Liste:
                        [{"kategorie": "...", "prioritaet": "Kritisch/Hoch/Mittel", "mangel": "...", "verstoss": "...", "massnahme": "...", "zeitstempel_sekunden": 0, "bild_index": 0}]
                        """
                        
                        # --- HIER IST DIE SCHLAUE SCHLEIFE ---
                        # Wir probieren die Modelle der Reihe nach durch.
                        # Wenn 3.0 nicht geht, nimmt er automatisch 2.0 oder 1.5
                        model_names = [
                            'gemini-3-pro-preview', 
                            'gemini-2.0-flash-exp', 
                            'gemini-1.5-pro',
                            'gemini-1.5-flash'
                        ]
                        
                        found_result = False
                        
                        for mn in model_names:
                            try:
                                model = genai.GenerativeModel(mn)
                                if st.session_state.m_type == "video":
                                    f = genai.upload_file(st.session_state.m_files[0])
                                    # Warten (Fix für Hänger)
                                    while f.state.name == "PROCESSING":
                                        time.sleep(2)
                                        f = genai.get_file(f.name)
                                    res = model.generate_content([f, prompt], generation_config={"response_mime_type": "application/json"})
                                else:
                                    # Öffne Bilder und konvertiere bei Bedarf
                                    imgs = []
                                    for p in st.session_state.m_files:
                                        try:
                                            img = Image.open(p)
                                            # Stelle sicher, dass Bild im RGB-Format ist
                                            if img.mode != 'RGB':
                                                img = img.convert('RGB')
                                            imgs.append(img)
                                        except Exception as e:
                                            st.warning(f"⚠️ Fehler beim Öffnen von {os.path.basename(p)}: {str(e)}")
                                            # Versuche mit cv2 als Fallback
                                            try:
                                                img_array = cv2.imread(p)
                                                if img_array is not None:
                                                    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                                                    img = Image.fromarray(img_rgb)
                                                    imgs.append(img)
                                            except:
                                                st.error(f"❌ Konnte Bild {os.path.basename(p)} nicht verarbeiten")
                                    
                                    if not imgs:
                                        st.error("❌ Keine Bilder konnten verarbeitet werden. Bitte versuchen Sie andere Dateiformate.")
                                        continue
                                    
                                    res = model.generate_content([prompt] + imgs, generation_config={"response_mime_type": "application/json"})
                                
                                # Wenn wir hier sind, hat es geklappt!
                                st.session_state.analysis_data = json.loads(clean_json(res.text))
                                found_result = True
                                break # Schleife beenden, wir haben ein Ergebnis
                            except:
                                continue # Fehler beim Modell? Nächstes probieren!
                        
                        if not found_result:
                            st.error("Alle KI-Modelle sind gerade ausgelastet oder nicht erreichbar. Bitte später versuchen.")
                        else:
                            st.rerun()
                            
                    except Exception as e: st.error(f"Fehler: {e}")

            if st.session_state.analysis_data:
                st.success(f"⚠️ {len(st.session_state.analysis_data)} Mängel gefunden")
                
                # Credits-Anzeige für Kunden (nicht Admin)
                if not is_admin() and st.session_state.username:
                    credits = get_customer_credits(st.session_state.username)
                    col_credits = st.columns([2, 1])
                    with col_credits[1]:
                        if credits < 1:
                            st.error(f"🪙 Credits: {credits} (Nicht genügend für Bericht!)")
                        else:
                            st.info(f"🪙 Verbleibende Credits: **{credits}**")
                    st.divider()
                
                st.markdown("### 📝 Projektdaten für Bericht")
                c_a, c_b = st.columns(2)
                with c_a:
                    proj = st.text_input("Projektname", value="Überbauung 'Luegisland', Wohlen AG")
                    insp = st.text_input("Inspektor Name", value="Dominik Marti")
                with c_b:
                    stat = st.selectbox("Status", ["⚠️ Massnahmen erforderlich", "✅ In Ordnung", "🛑 Kritisch - Baustopp"])
                st.divider()

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
                        # Credit-Prüfung (nur für Kunden, nicht für Admin)
                        if not is_admin():
                            username = st.session_state.username
                            credits = get_customer_credits(username)
                            if credits < 1:
                                st.error(f"⚠️ Nicht genügend Credits! Sie haben {credits} Credit(s). Bitte kontaktieren Sie den Administrator.")
                            else:
                                # Credit abbuchen
                                if deduct_credit(username):
                                    st.success(f"✅ 1 Credit abgebucht. Verbleibend: {credits - 1}")
                                    st.session_state.confirmed = confirmed
                                    st.session_state.meta_p = proj
                                    st.session_state.meta_i = insp
                                    st.session_state.meta_s = stat
                                    st.session_state.app_step = 'screen_c'
                                    st.rerun()
                                else:
                                    st.error("⚠️ Fehler beim Abziehen der Credits. Bitte versuchen Sie es erneut.")
                        else:
                            # Admin kann ohne Credits erstellen
                            st.session_state.confirmed = confirmed
                            st.session_state.meta_p = proj
                            st.session_state.meta_i = insp
                            st.session_state.meta_s = stat
                            st.session_state.app_step = 'screen_c'
                            st.rerun()

        elif st.session_state.app_step == 'screen_c':
            st.subheader("Berichte fertig!")
            
            # Credits-Anzeige nach erfolgreicher Erstellung (für Kunden)
            if not is_admin() and st.session_state.username:
                remaining_credits = get_customer_credits(st.session_state.username)
                st.info(f"🪙 Verbleibende Credits: **{remaining_credits}**")
                st.divider()
            
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

            st.divider()
            st.markdown("### 📧 Versenden")
            email_to = st.text_input("Empfänger Email", placeholder="kunde@bau.ch")
            
            if email_to:
                subject = f"Sicherheitsbericht: {p}"
                body = f"Grüezi,\n\nanbei erhalten Sie den Sicherheitsbericht für das Projekt {p}.\n\nInspektor: {i}\nStatus: {s}\n\nFreundliche Grüsse\nSafeSite Drohne"
                safe_s = urllib.parse.quote(subject)
                safe_b = urllib.parse.quote(body)
                mailto = f"mailto:{email_to}?subject={safe_s}&body={safe_b}"
                
                st.link_button("📧 Email-Programm öffnen", mailto)

            if st.button("Neuer Auftrag"):
                st.session_state.app_step = 'screen_a'
                st.session_state.analysis_data = []
                st.rerun()

elif st.session_state.current_page == 'suva':
    st.header("📋 Die 8 lebenswichtigen Regeln (SUVA)")
    
    suva_regeln = [
        {"titel": "1. Absturzkanten sichern", "desc": "Ab 2.0m Absturzhöhe sind Seitenschutz oder Auffangeinrichtungen zwingend.", "img": "regel_1.png"},
        {"titel": "2. Bodenöffnungen", "desc": "Jede Öffnung muss durchbruchsicher abgedeckt und fixiert sein.", "img": "regel_2.png"},
        {"titel": "3. Lasten anschlagen", "desc": "Lasten nur von instruiertem Personal anschlagen. Niemals unter schwebenden Lasten.", "img": "regel_3.png"},
        {"titel": "4. Fassadengerüste", "desc": "Ab 3.0m Absturzhöhe ist ein Fassadengerüst erforderlich.", "img": "regel_4.png"},
        {"titel": "5. Gerüstkontrolle", "desc": "Tägliche Sichtkontrolle durch den Benutzer. Beläge müssen dicht sein.", "img": "regel_5.png"},
        {"titel": "6. Sichere Zugänge", "desc": "Treppentürme sind Leitern vorzuziehen. Leitern gegen Wegrutschen sichern.", "img": "regel_6.png"},
        {"titel": "7. PSA tragen", "desc": "Helm und Sicherheitsschuhe sind Pflicht. Je nach Situation: Weste, Brille, Gehörschutz.", "img": "regel_7.png"},
        {"titel": "8. Gräben sichern", "desc": "Ab 1.50m Tiefe müssen Gräben gespriesst oder geböscht werden.", "img": "regel_8.png"}
    ]

    for r in suva_regeln:
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                if os.path.exists(r["img"]):
                    st.image(r["img"], use_container_width=True)
                else:
                    st.info("🖼️ Bild fehlt")
            with c2:
                st.subheader(r["titel"])
                st.write(r["desc"])

elif st.session_state.current_page == 'bauav':
    st.header("⚖️ Bauarbeitenverordnung (BauAV)")
    st.write("Die wichtigsten Artikel für den Hochbau:")

    def bauav_item(nr, titel, text):
        with st.expander(f"Art. {nr} - {titel}"):
            st.write(text)

    bauav_item(3, "Planung und Organisation", "Die Arbeiten müssen so geplant werden, dass die Sicherheit gewährleistet ist. Ordnung auf der Baustelle ist Pflicht.")
    bauav_item(10, "Verkehrswege", "Verkehrswege müssen sicher begehbar sein. Hindernisse und Stolperstellen sind zu entfernen.")
    bauav_item(12, "Absperrung", "Die Baustelle muss gegen unbefugtes Betreten gesichert sein (Zäune, Signale).")
    bauav_item(17, "Absturzsicherung", "Absturzkanten sind ab 2.0m Höhe zu sichern (Seitenschutz). Bei Dächern ab 3.0m.")
    bauav_item(19, "Herabfallende Gegenstände", "Schutz vor herabfallendem Material (Schutzdächer, Absperrungen).")
    bauav_item(20, "Gräben und Schächte", "Wände von Gräben müssen ab 1.50m Tiefe gesichert (verspriesst/geböscht) werden.")
    bauav_item(22, "Ordnung", "Materialien sind stabil zu lagern. Keine Gefährdung durch Umkippen oder Wegrollen.")
    bauav_item(47, "Gerüste", "Gerüste müssen standfest sein und über sichere Zugänge verfügen. Beläge lückenlos.")

elif st.session_state.current_page == 'kunden':
    if not is_admin():
        st.error("⛔ Zugriff verweigert. Diese Seite ist nur für Administratoren verfügbar.")
        st.info("Bitte als Admin einloggen, um auf die Kundenverwaltung zuzugreifen.")
    else:
        st.header("👥 Kundenverwaltung")
        st.markdown("---")
        
        customers = load_customers()
        
        # Tab-Layout
        tab1, tab2 = st.tabs(["📋 Kundenliste", "➕ Neuen Kunden hinzufügen"])
        
        with tab1:
            st.subheader("Alle Kunden")
            if not customers:
                st.info("Noch keine Kunden vorhanden. Fügen Sie einen neuen Kunden hinzu.")
            else:
                users = load_users()
                for kunde_id, kunde_data in customers.items():
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"### {kunde_data.get('name', 'Unbekannt')}")
                            st.write(f"**Firma:** {kunde_data.get('firma', '-')}")
                            email = kunde_data.get('email', '')
                            st.write(f"**Email:** {email}")
                            st.write(f"**Telefon:** {kunde_data.get('telefon', '-')}")
                            if 'adresse' in kunde_data:
                                st.write(f"**Adresse:** {kunde_data['adresse']}")
                            
                            # Credits anzeigen
                            credits = int(kunde_data.get('credits', 0))
                            st.metric("🪙 SafeSite Credits", credits)
                            
                            # Login-Status anzeigen
                            if email and email in users:
                                st.success("✅ Login aktiv")
                                st.caption(f"Username: {email}")
                            else:
                                st.warning("⚠️ Kein Login erstellt")
                        with col2:
                            if email and email in users:
                                if st.button("🔑 Passwort ändern", key=f"passwd_{kunde_id}"):
                                    st.session_state[f"edit_passwd_{kunde_id}"] = True
                                    st.rerun()
                            else:
                                if st.button("🔑 Login erstellen", key=f"create_login_{kunde_id}"):
                                    st.session_state[f"create_login_{kunde_id}"] = True
                                    st.rerun()
                            # Credits bearbeiten Button
                            if st.button("💰 Credits verwalten", key=f"credits_{kunde_id}"):
                                st.session_state[f"edit_credits_{kunde_id}"] = True
                                st.rerun()
                        with col3:
                            if st.button("🗑️ Löschen", key=f"delete_{kunde_id}"):
                                # Kunde aus customers.json löschen
                                del customers[kunde_id]
                                save_customers(customers)
                                # Login aus users.json löschen (falls vorhanden)
                                if email and email in users:
                                    del users[email]
                                    save_users(users)
                                st.success("Kunde gelöscht!")
                                st.rerun()
                        
                        # Credits bearbeiten Formular
                        if st.session_state.get(f"edit_credits_{kunde_id}", False):
                            st.divider()
                            with st.form(f"form_credits_{kunde_id}"):
                                st.markdown("**🪙 Credits verwalten**")
                                current_credits = int(kunde_data.get('credits', 0))
                                new_credits = st.number_input("Anzahl Credits", min_value=0, value=current_credits, step=1, key=f"credits_input_{kunde_id}")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Credits speichern", use_container_width=True):
                                        update_customer_credits(kunde_id, new_credits)
                                        st.session_state[f"edit_credits_{kunde_id}"] = False
                                        st.success(f"Credits auf {new_credits} aktualisiert!")
                                        st.rerun()
                                with col_b:
                                    if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                                        st.session_state[f"edit_credits_{kunde_id}"] = False
                                        st.rerun()
                        
                        # Passwort ändern Formular
                        if st.session_state.get(f"edit_passwd_{kunde_id}", False):
                            st.divider()
                            with st.form(f"form_passwd_{kunde_id}"):
                                new_pass = st.text_input("Neues Passwort", type="password", key=f"new_pass_{kunde_id}")
                                new_pass_confirm = st.text_input("Passwort bestätigen", type="password", key=f"new_pass_confirm_{kunde_id}")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Passwort ändern", use_container_width=True):
                                        if new_pass and new_pass == new_pass_confirm:
                                            users[email] = new_pass
                                            save_users(users)
                                            st.session_state[f"edit_passwd_{kunde_id}"] = False
                                            st.success("Passwort erfolgreich geändert!")
                                            st.rerun()
                                        elif new_pass != new_pass_confirm:
                                            st.error("Passwörter stimmen nicht überein!")
                                        else:
                                            st.error("Passwort darf nicht leer sein!")
                                with col_b:
                                    if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                                        st.session_state[f"edit_passwd_{kunde_id}"] = False
                                        st.rerun()
                        
                        # Login erstellen Formular
                        if st.session_state.get(f"create_login_{kunde_id}", False):
                            st.divider()
                            with st.form(f"form_create_login_{kunde_id}"):
                                st.info(f"Login wird für: {email} erstellt")
                                new_pass = st.text_input("Passwort", type="password", key=f"create_pass_{kunde_id}")
                                new_pass_confirm = st.text_input("Passwort bestätigen", type="password", key=f"create_pass_confirm_{kunde_id}")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Login erstellen", use_container_width=True):
                                        if new_pass and new_pass == new_pass_confirm:
                                            users[email] = new_pass
                                            save_users(users)
                                            st.session_state[f"create_login_{kunde_id}"] = False
                                            st.success(f"Login für {email} erfolgreich erstellt!")
                                            st.rerun()
                                        elif new_pass != new_pass_confirm:
                                            st.error("Passwörter stimmen nicht überein!")
                                        else:
                                            st.error("Passwort darf nicht leer sein!")
                                with col_b:
                                    if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                                        st.session_state[f"create_login_{kunde_id}"] = False
                                        st.rerun()
                        
                        st.divider()
        
        with tab2:
            st.subheader("Neuen Kunden hinzufügen")
            with st.form("neuer_kunde", clear_on_submit=True):
                kunde_name = st.text_input("Name *", placeholder="Max Mustermann")
                firma = st.text_input("Firma", placeholder="Mustermann AG")
                email = st.text_input("Email *", placeholder="max@mustermann.ch")
                telefon = st.text_input("Telefon", placeholder="+41 79 123 45 67")
                adresse = st.text_area("Adresse", placeholder="Musterstrasse 123\n8000 Zürich")
                
                st.divider()
                st.markdown("**🪙 SafeSite Credits:**")
                initial_credits = st.number_input("Anfangliche Credits", min_value=0, value=0, step=1, key="new_kunde_credits")
                st.caption("💡 1 Credit = 1 Bericht. Credits werden automatisch bei jedem Bericht abgebucht.")
                
                st.divider()
                st.markdown("**Login für SafeSite-Check (optional):**")
                create_login = st.checkbox("Login-Konto für diesen Kunden erstellen", value=False)
                login_passwort = ""
                login_passwort_confirm = ""
                if create_login:
                    login_passwort = st.text_input("Passwort", type="password", key="new_kunde_pass")
                    login_passwort_confirm = st.text_input("Passwort bestätigen", type="password", key="new_kunde_pass_confirm")
                    email_placeholder = email if email else "(Email eingeben)"
                    st.caption(f"💡 Der Kunde kann sich dann mit der Email '{email_placeholder}' als Username anmelden.")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("✅ Kunde hinzufügen", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("❌ Abbrechen", use_container_width=True)
                
                if submit:
                    if not kunde_name or not email:
                        st.error("⚠️ Name und Email sind Pflichtfelder!")
                    elif create_login and (not login_passwort or login_passwort != login_passwort_confirm):
                        if not login_passwort:
                            st.error("⚠️ Bitte geben Sie ein Passwort ein, wenn Sie ein Login erstellen möchten!")
                        else:
                            st.error("⚠️ Die Passwörter stimmen nicht überein!")
                    else:
                        # Prüfen ob Email bereits als Username existiert
                        users = load_users()
                        if email in users:
                            st.error(f"⚠️ Ein Login mit der Email '{email}' existiert bereits!")
                        else:
                            # Eindeutige ID generieren
                            kunde_id = str(uuid.uuid4())[:8]
                            
                            # Kunde hinzufügen
                            customers[kunde_id] = {
                                "name": kunde_name,
                                "firma": firma,
                                "email": email,
                                "telefon": telefon,
                                "adresse": adresse,
                                "credits": int(initial_credits),
                                "erstellt_am": date.today().strftime('%d.%m.%Y')
                            }
                            save_customers(customers)
                            
                            # Login erstellen, falls gewünscht
                            if create_login and login_passwort:
                                users[email] = login_passwort
                                save_users(users)
                                st.success(f"✅ Kunde '{kunde_name}' erfolgreich hinzugefügt mit {initial_credits} Credits und Login erstellt!")
                            else:
                                st.success(f"✅ Kunde '{kunde_name}' erfolgreich hinzugefügt mit {initial_credits} Credits!")
                            st.rerun()
