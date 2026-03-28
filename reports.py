"""
SafeSite Drohne – Berichterstellung (PDF & Word)
"""
import os
import time
import cv2
from datetime import date
from fpdf import FPDF
from config import LOGO_FILE

try:
    from docx import Document
    from docx.shared import Inches
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False


def extract_frame(video_path: str, timestamp: float):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = total / fps if fps > 0 else 30
        timestamp = max(0, min(float(timestamp), duration - 0.5))
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception:
        pass
    return None


def _safe(text) -> str:
    if text is None:
        return ""
    return str(text).encode("latin-1", "ignore").decode("latin-1")


def _get_image(item, index, m_type, m_files):
    if m_type == "video":
        frame = extract_frame(m_files[0], item.get("zeitstempel_sekunden", 0))
        if frame is not None:
            path = f"temp_report_{index}.jpg"
            cv2.imwrite(path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            return path, True
    elif m_type == "images":
        idx = item.get("bild_index", 0)
        if idx < len(m_files):
            return m_files[idx], False
    return None, False


class _PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try:
                self.image(LOGO_FILE, 160, 8, 40)
            except Exception:
                pass
        self.ln(30)


def create_pdf(data, m_type, m_files, projekt, inspektor, status):
    pdf = _PDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SICHERHEITS-INSPEKTION (DROHNE)", ln=True)
    pdf.ln(8)

    for label, val in [
        ("Projekt:", _safe(projekt)),
        ("Datum:", f"{date.today().strftime('%d.%m.%Y')} | {time.strftime('%H:%M')} Uhr"),
        ("Inspektor:", _safe(f"{inspektor} (SafeSite Drohne)")),
    ]:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(35, 8, label, ln=0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, val, ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 8, "Status:", ln=0)
    pdf.set_font("Arial", "", 11)
    if "Massnahmen" in status:
        pdf.set_text_color(255, 153, 51)
    elif "Kritisch" in status:
        pdf.set_text_color(204, 0, 0)
    else:
        pdf.set_text_color(0, 153, 0)
    pdf.cell(0, 8, _safe(status), ln=True)
    pdf.set_text_color(0, 0, 0)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "1. ZUSAMMENFASSUNG / MAENGELLISTE", ln=True)
    pdf.ln(5)

    temps = []
    for i, item in enumerate(data):
        if pdf.get_y() > 220:
            pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(204, 0, 0)
        pdf.cell(0, 8, f"{i+1}. {_safe(item.get('kategorie','Mangel'))} ({_safe(item.get('prioritaet','Mittel'))})", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, f"Mangel: {_safe(item.get('mangel','-'))}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Verstoss: {_safe(item.get('verstoss','-'))}")
        pdf.ln(2)
        pdf.multi_cell(0, 5, f"Massnahme: {_safe(item.get('massnahme','-'))}")
        pdf.ln(5)
        img, is_temp = _get_image(item, i, m_type, m_files)
        if img:
            try:
                pdf.image(img, x=20, w=120)
            except Exception:
                pass
            pdf.ln(10)
            if is_temp:
                temps.append(img)

    if pdf.get_y() > 200:
        pdf.add_page()
    pdf.ln(15)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "4. FREIGABE", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Dieser Bericht wurde generiert durch SafeSite Drohne.", ln=True)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Hinweis: Dieser Bericht dient als visuelle Unterstuetzung. Er entbindet die zustaendige Bauleitung nicht von der gesetzlichen Kontrollpflicht.")
    pdf.ln(20)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 10, "Erstellt durch:", ln=0)
    pdf.set_font("Arial", "", 11)
    pdf.cell(65, 10, _safe(inspektor), ln=0)
    pdf.cell(0, 10, "_______________________ (Datum/Unterschrift)", ln=True, align="R")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 10, "Verantwortlicher:", ln=0)
    pdf.set_font("Arial", "", 11)
    pdf.cell(65, 10, "Bauleitung / Polier", ln=0)
    pdf.cell(0, 10, "_______________________ (Datum/Unterschrift)", ln=True, align="R")

    out = "Bericht.pdf"
    pdf.output(out)
    for t in temps:
        try:
            os.remove(t)
        except Exception:
            pass
    return out


def create_word(data, m_type, m_files, projekt, inspektor, status):
    if not WORD_AVAILABLE:
        return None
    doc = Document()
    if os.path.exists(LOGO_FILE):
        try:
            doc.add_picture(LOGO_FILE, width=Inches(1.5))
            doc.paragraphs[-1].alignment = 2
        except Exception:
            pass
    doc.add_heading("SICHERHEITS-INSPEKTION (DROHNE)", 0)
    p = doc.add_paragraph()
    p.add_run("Projekt: ").bold = True
    p.add_run(f"{projekt}\n")
    p.add_run("Datum: ").bold = True
    p.add_run(f"{date.today().strftime('%d.%m.%Y')}\n")
    p.add_run("Inspektor: ").bold = True
    p.add_run(f"{inspektor}\n")
    p.add_run("Status: ").bold = True
    p.add_run(status)
    doc.add_heading("1. ZUSAMMENFASSUNG / MAENGEL", level=1)
    temps = []
    for i, item in enumerate(data):
        doc.add_heading(f"{i+1}. {item.get('kategorie','Mangel')}", level=2)
        p = doc.add_paragraph()
        p.add_run("Mangel: ").bold = True
        p.add_run(f"{item.get('mangel','-')}\n")
        p.add_run("Verstoss: ").bold = True
        p.add_run(f"{item.get('verstoss','-')}\n")
        p.add_run("Massnahme: ").bold = True
        p.add_run(item.get("massnahme", "-"))
        img, is_temp = _get_image(item, i, m_type, m_files)
        if img:
            try:
                doc.add_picture(img, width=Inches(4.5))
            except Exception:
                pass
            if is_temp:
                temps.append(img)
    doc.add_page_break()
    doc.add_heading("4. FREIGABE", level=1)
    doc.add_paragraph("Dieser Bericht wurde generiert durch SafeSite Drohne.")
    p = doc.add_paragraph("Hinweis: Dient als visuelle Unterstuetzung.")
    p.italic = True
    doc.add_paragraph(f"\nErstellt durch: {inspektor} \t____________________")
    doc.add_paragraph("\nVerantwortlicher: \t\t\t____________________")
    out = "Bericht.docx"
    doc.save(out)
    for t in temps:
        try:
            os.remove(t)
        except Exception:
            pass
    return out
