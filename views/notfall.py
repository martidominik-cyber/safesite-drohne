"""Notfallmanagement – Notfallnummern und W-Fragen"""
import streamlit as st
from db import get_notfall, add_notfall, delete_notfall


def render_notfall():
    st.header("🚨 Notfallmanagement (SOS)")
    st.markdown("**Wenn etwas passiert, zählt jede Sekunde.**")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📞 Notfallnummern", "➕ Neuen Kontakt hinzufügen"])

    with tab1:
        _render_kontakte()

    with tab2:
        _render_neuer_kontakt()


def _render_kontakte():
    st.subheader("Ihre Notfallkontakte")
    notfall = get_notfall()

    # Sichtbarkeitsfilter
    visible = {}
    for nid, data in notfall.items():
        owner = data.get("owner", "all")
        if owner == "all" or (st.session_state.logged_in and owner == st.session_state.username):
            visible[nid] = data

    if not visible:
        st.info("Keine Notfallkontakte gefunden.")
        return

    cols = st.columns(2)
    for idx, (nid, data) in enumerate(visible.items()):
        with cols[idx % 2]:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"### {data.get('icon', '📞')} {data.get('name', 'Unbekannt')}")
                with c2:
                    if st.session_state.logged_in and data.get("owner") == st.session_state.username:
                        if st.button("🗑️", key=f"del_n_{nid}"):
                            delete_notfall(nid)
                            st.rerun()
                st.markdown(data.get("desc", ""))
                tel = data.get("tel", "")
                st.markdown(f"[📞 {tel} anrufen](tel:{tel})")
            st.markdown("")

    st.markdown("---")

    # W-Fragen
    st.subheader("❓ Die W-Fragen-Hilfe")
    st.info("💡 Viele Leute stehen unter Schock. Ein kurzes Skript hilft:")
    with st.container(border=True):
        st.markdown("#### Beantworten Sie diese Fragen am Telefon:")
        for frage, hilfe in [
            ("Wer ruft an?", "Ihr Name und Ihre Funktion"),
            ("Wo ist es passiert?", "Genauer Standort, Adresse, Baustelle"),
            ("Was ist passiert?", "Art des Unfalls, Verletzungen"),
            ("Wie viele Verletzte?", "Anzahl der betroffenen Personen"),
        ]:
            st.markdown(f"**{frage}**")
            st.caption(hilfe)
            st.markdown("")

    st.warning("⚠️ Bleiben Sie ruhig, sprechen Sie langsam. "
               "Legen Sie nicht auf, bis die Leitstelle alle Informationen hat.")


def _render_neuer_kontakt():
    if not st.session_state.logged_in:
        st.warning("⚠️ Bitte einloggen, um eigene Notfallkontakte hinzuzufügen.")
        return

    st.subheader("Eigenen Notfallkontakt hinterlegen")
    st.info("Diese Kontakte sind **nur für Sie** sichtbar.")

    with st.form("neuer_notfall", clear_on_submit=True):
        name = st.text_input("Name des Kontakts *", placeholder="z.B. Bauleiter Herr Müller")
        tel = st.text_input("Telefonnummer *", placeholder="z.B. 079 123 45 67")
        desc = st.text_area("Beschreibung", placeholder="z.B. Bei Fragen zur Statik")
        icon = st.selectbox("Icon", ["📞", "👷", "👨‍⚕️", "🏥", "🏢", "🚨", "📱", "☎️", "🚑"])

        if st.form_submit_button("Kontakt hinzufügen", type="primary", use_container_width=True):
            if not name or not tel:
                st.error("❌ Name und Telefonnummer sind Pflichtfelder!")
            else:
                add_notfall(name, tel, desc, icon, st.session_state.username)
                st.success(f"✅ '{name}' hinzugefügt!")
                st.rerun()
