"""Startseite"""
import os
import streamlit as st
from config import TITELBILD_FILE
from auth import is_admin


def render_home():
    if os.path.exists(TITELBILD_FILE):
        st.image(TITELBILD_FILE, use_container_width=True)

    st.header("Willkommen bei SafeSite Drohne")
    st.markdown("## Sicherheit, die sich auszahlt.")
    st.markdown(
        "SafeSite Drohne ist mehr als nur eine Kamera in der Luft. "
        "Wir liefern Ihnen ein komplettes System zur Unfallprävention "
        "und Dokumentation – entwickelt von Polieren für den täglichen Einsatz."
    )
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("")

    buttons = [
        ("safesite", "🔍 SafeSite-Check", True),
        ("suva", "📋 SUVA Regeln", False),
        ("bauav", "⚖️ BauAV", False),
        ("notfall", "🚨 Notfallmanagement", False),
        ("gefahrstoff", "🧪 Gefahrstoffkataster", False),
        ("wetter", "🌤️ Wetter-Warnungen", False),
        ("preise", "💎 Preise", False),
    ]

    # 3 Spalten pro Zeile
    for row_start in range(0, len(buttons), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(buttons):
                page_key, label, primary = buttons[idx]
                with col:
                    kwargs = {"use_container_width": True}
                    if primary:
                        kwargs["type"] = "primary"
                    if st.button(label, key=f"nav_{page_key}", **kwargs):
                        st.session_state.current_page = page_key
                        st.rerun()
        st.markdown("")

    if is_admin():
        st.markdown("")
        c = st.columns([1, 1, 1])
        with c[1]:
            if st.button("👥 Kundenverwaltung", use_container_width=True):
                st.session_state.current_page = "kunden"
                st.rerun()
