"""SafeSite-Check – Upload, Analyse, Bericht"""
import os
import urllib.parse
import streamlit as st

from auth import is_admin
from db import get_credits, deduct_credit
from ai_engine import run_analysis
from reports import create_pdf, create_word, WORD_AVAILABLE, extract_frame
from utils import save_uploaded_file, convert_image_if_needed, cleanup_temp_files


def render_check():
    if not st.session_state.logged_in:
        st.header("🔍 SafeSite-Check")
        st.warning("⚠️ Sie müssen sich anmelden, um den SafeSite-Check zu verwenden.")
        return

    step = st.session_state.app_step

    if step == "upload":
        _render_upload()
    elif step == "analyse":
        _render_analyse()
    elif step == "bericht":
        _render_bericht()


# ============================================================
# SCHRITT 1: Upload
# ============================================================
def _render_upload():
    st.subheader("Neuer Auftrag")
    mode = st.radio("Quelle:", ["📹 Video", "📸 Fotos"], horizontal=True)

    if mode == "📹 Video":
        st.info("💡 Auf mobilen Geräten wählen Sie Videos über den Datei-Explorer aus.")
        vf = st.file_uploader("Video hochladen", type=["mp4", "mov", "avi"])
        if vf:
            st.success(f"✅ Video ausgewählt: {vf.name}")
            if st.button("Analyse starten", type="primary", use_container_width=True):
                try:
                    path = save_uploaded_file(vf)
                    st.session_state.m_type = "video"
                    st.session_state.m_files = [path]
                    st.session_state.app_step = "analyse"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Hochladen: {e}")
    else:
        st.info("💡 Auf mobilen Geräten wählen Sie Fotos über den Datei-Explorer aus.")
        pf = st.file_uploader(
            "Fotos hochladen",
            type=["jpg", "jpeg", "png", "heic", "heif", "webp"],
            accept_multiple_files=True,
        )
        if pf:
            st.success(f"✅ {len(pf)} Foto(s) ausgewählt")
            for f in pf[:5]:
                st.caption(f"📷 {f.name}")
            if len(pf) > 5:
                st.caption(f"... und {len(pf) - 5} weitere")

            if st.button("Analyse starten", type="primary", use_container_width=True):
                with st.spinner("Bilder werden verarbeitet..."):
                    try:
                        paths = []
                        for f in pf:
                            path = save_uploaded_file(f)
                            path = convert_image_if_needed(path)
                            paths.append(path)
                        st.session_state.m_type = "images"
                        st.session_state.m_files = paths
                        st.session_state.app_step = "analyse"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")
                        cleanup_temp_files(paths if 'paths' in dir() else [])


# ============================================================
# SCHRITT 2: KI-Analyse + Bestätigung
# ============================================================
def _render_analyse():
    st.subheader("🕵️ KI-Analyse")

    # Medien anzeigen
    if st.session_state.m_type == "video":
        st.video(st.session_state.m_files[0])
    else:
        cols = st.columns(3)
        for i, f in enumerate(st.session_state.m_files):
            with cols[i % 3]:
                st.image(f, caption=f"Bild {i+1}")

    # Analyse starten (nur wenn noch keine Daten)
    if not st.session_state.analysis_data:
        st.session_state.analysis_data = run_analysis(
            st.session_state.m_type,
            st.session_state.m_files,
        )
        if st.session_state.analysis_data:
            st.rerun()
        return

    # Ergebnisse anzeigen
    total = len(st.session_state.analysis_data)
    confirmed_count = sum(1 for f in st.session_state.analysis_data
                          if f.get("verifikation_label", "").startswith("✅✅"))
    st.success(f"⚠️ {total} Mängel gefunden"
               + (f" — davon {confirmed_count} durch Dual-AI bestätigt" if confirmed_count else ""))

    # Credits (nur für Kunden)
    if not is_admin() and st.session_state.username:
        credits = get_credits(st.session_state.username)
        col_a, col_b = st.columns([2, 1])
        with col_b:
            if credits < 1:
                st.error(f"🪙 Credits: {credits} (Nicht genügend!)")
            else:
                st.info(f"🪙 Credits: **{credits}**")
        st.divider()

    # Projektdaten
    st.markdown("### 📝 Projektdaten für Bericht")
    c_a, c_b = st.columns(2)
    with c_a:
        proj = st.text_input("Projektname", value="Baustelle, Ort")
        insp = st.text_input("Inspektor Name", value="Dominik Marti")
    with c_b:
        stat = st.selectbox("Status", [
            "⚠️ Massnahmen erforderlich",
            "✅ In Ordnung",
            "🛑 Kritisch - Baustopp",
        ])
    st.divider()

    # Mängel bestätigen
    with st.form("check_form"):
        confirmed = []
        for i, item in enumerate(st.session_state.analysis_data):
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.session_state.m_type == "video":
                    frm = extract_frame(st.session_state.m_files[0], item.get("zeitstempel_sekunden", 0))
                    if frm is not None:
                        st.image(frm)
                else:
                    idx = item.get("bild_index", 0)
                    if idx < len(st.session_state.m_files):
                        st.image(st.session_state.m_files[idx])
            with c2:
                # Verification-Label anzeigen
                verif_label = item.get("verifikation_label", "")
                if verif_label:
                    st.caption(verif_label)
                st.markdown(f":orange[**{item.get('prioritaet')}: {item.get('mangel')}**]")
                st.write(item.get("massnahme"))
                # Verification-Detail falls vorhanden
                verif_detail = item.get("verifikation_detail", "")
                if verif_detail:
                    st.caption(f"📋 {verif_detail}")
                if st.checkbox("Aufnehmen", True, key=f"check_{i}"):
                    confirmed.append(item)
            st.divider()

        if st.form_submit_button("Berichte erstellen", type="primary"):
            # Credit-Prüfung
            if not is_admin():
                credits = get_credits(st.session_state.username)
                if credits < 1:
                    st.error(f"⚠️ Nicht genügend Credits ({credits})!")
                    return
                if not deduct_credit(st.session_state.username):
                    st.error("⚠️ Fehler beim Abziehen der Credits.")
                    return
                st.success(f"✅ 1 Credit abgebucht. Verbleibend: {credits - 1}")

            st.session_state.confirmed = confirmed
            st.session_state.meta_p = proj
            st.session_state.meta_i = insp
            st.session_state.meta_s = stat
            st.session_state.app_step = "bericht"
            st.rerun()


# ============================================================
# SCHRITT 3: Berichte herunterladen
# ============================================================
def _render_bericht():
    st.subheader("Berichte fertig!")

    if not is_admin() and st.session_state.username:
        from db import get_credits
        st.info(f"🪙 Verbleibende Credits: **{get_credits(st.session_state.username)}**")
        st.divider()

    p = st.session_state.get("meta_p", "")
    i = st.session_state.get("meta_i", "")
    s = st.session_state.get("meta_s", "")
    confirmed = st.session_state.get("confirmed", [])

    # PDF erstellen (einmalig)
    if not st.session_state.pdf_file_path:
        try:
            st.session_state.pdf_file_path = create_pdf(
                confirmed, st.session_state.m_type, st.session_state.m_files, p, i, s
            )
        except Exception as e:
            st.error(f"❌ PDF-Fehler: {e}")

    # Word erstellen (einmalig)
    if not st.session_state.word_file_path and WORD_AVAILABLE:
        try:
            st.session_state.word_file_path = create_word(
                confirmed, st.session_state.m_type, st.session_state.m_files, p, i, s
            )
        except Exception as e:
            st.warning(f"⚠️ Word-Fehler: {e}")

    # Downloads
    c1, c2 = st.columns(2)
    with c1:
        pdf_path = st.session_state.pdf_file_path
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("📄 PDF Bericht", f, "SSD_Bericht.pdf",
                                   mime="application/pdf", use_container_width=True)
    with c2:
        word_path = st.session_state.word_file_path
        if word_path and os.path.exists(word_path):
            with open(word_path, "rb") as f:
                st.download_button("📝 Word Bericht", f, "SSD_Bericht.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)

    # Email versenden
    st.divider()
    st.markdown("### 📧 Versenden")
    email_to = st.text_input("Empfänger Email", placeholder="kunde@bau.ch")
    if email_to:
        subject = urllib.parse.quote(f"Sicherheitsbericht: {p}")
        body = urllib.parse.quote(
            f"Grüezi,\n\nanbei der Sicherheitsbericht für {p}.\n\n"
            f"Inspektor: {i}\nStatus: {s}\n\nFreundliche Grüsse\nSafeSite Drohne"
        )
        st.link_button("📧 Email-Programm öffnen", f"mailto:{email_to}?subject={subject}&body={body}")

    # Neuer Auftrag
    if st.button("Neuer Auftrag", use_container_width=True):
        from auth import reset_check
        reset_check()
        st.rerun()
