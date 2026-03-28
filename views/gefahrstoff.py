"""Gefahrstoffkataster – Verwaltung von Gefahrstoffen"""
import streamlit as st
from auth import is_admin
from db import get_gefahrstoffe, add_gefahrstoff, delete_gefahrstoff


def render_gefahrstoff():
    st.header("🧪 Gefahrstoffkataster")
    st.markdown("**Digitaler Zugriff auf Sicherheitsdatenblätter.**")

    with st.expander("ℹ️ Wichtige Hinweise für die Praxis", expanded=False):
        st.markdown(
            "**Sicherheitsdatenblatt-Pflicht:** Jeder Mitarbeiter muss jederzeit digital Zugriff haben.\n\n"
            "**Mengen-Schwelle:** Für gewerblich genutzte Produkte muss ein Kataster geführt werden.\n\n"
            "**Substitution:** Prüfen Sie: Kann der Stoff durch einen harmloseren ersetzt werden?"
        )

    st.markdown("---")
    query = st.text_input("🔍 Suche", placeholder="z.B. Beton, Lösungsmittel, Kleber...")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Gefahrstoffliste", "➕ Neuen hinzufügen"])

    with tab1:
        _render_liste(query)
    with tab2:
        _render_neuer()


def _render_liste(query):
    gefahrstoffe = get_gefahrstoffe()

    if not gefahrstoffe:
        st.info("Noch keine Gefahrstoffe vorhanden.")
        return

    count = 0
    for gid, data in gefahrstoffe.items():
        # Sichtbarkeit
        owner = data.get("owner", "all")
        if not is_admin() and owner != "all" and owner != st.session_state.username:
            continue

        # Suchfilter
        if query:
            q = query.lower()
            searchable = " ".join(str(data.get(f, "")) for f in [
                "name", "handelsbezeichnung", "kategorie", "cas_nummer",
                "hersteller", "lagerort", "gefahrenbeschreibung"
            ]).lower()
            if q not in searchable:
                continue

        count += 1
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### {data.get('handelsbezeichnung', data.get('name', '?'))}")
            with c2:
                can_del = is_admin() or (st.session_state.logged_in and owner == st.session_state.username)
                if can_del and st.button("🗑️", key=f"del_g_{gid}"):
                    delete_gefahrstoff(gid)
                    st.rerun()

            with st.expander("📋 Alle Details"):
                c1, c2 = st.columns(2)
                with c1:
                    for label, key in [
                        ("Hersteller", "hersteller"), ("Kategorie", "kategorie"),
                        ("CAS-Nummer", "cas_nummer"), ("Lagerort", "lagerort"),
                        ("Menge", "menge"), ("SDB Datum", "sdb_datum"),
                    ]:
                        val = data.get(key)
                        if val:
                            st.markdown(f"**{label}:** {val}")
                with c2:
                    if data.get("ghs_symbole"):
                        st.markdown(f"**GHS-Symbole:** {data['ghs_symbole']}")
                    if data.get("gefahrenbeschreibung"):
                        st.markdown("**Gefahren:**")
                        st.write(data["gefahrenbeschreibung"])
                    if data.get("schutzmassnahmen"):
                        st.markdown("**Schutzmassnahmen:**")
                        st.write(data["schutzmassnahmen"])

                if data.get("sdb_link"):
                    st.markdown(f"📄 [Sicherheitsdatenblatt öffnen]({data['sdb_link']})")

            # Kurzübersicht
            c1, c2 = st.columns(2)
            with c1:
                if data.get("kategorie"):
                    st.caption(f"📦 {data['kategorie']}")
            with c2:
                if data.get("ghs_symbole"):
                    st.caption(f"⚠️ {data['ghs_symbole']}")

    if query and count == 0:
        st.info("💡 Keine Gefahrstoffe gefunden.")


def _render_neuer():
    if not st.session_state.logged_in:
        st.warning("⚠️ Bitte einloggen.")
        return

    st.subheader("Neuen Gefahrstoff hinzufügen")

    with st.form("neuer_gefahrstoff", clear_on_submit=True):
        handelsbezeichnung = st.text_input("Handelsbezeichnung *")
        hersteller = st.text_input("Hersteller *")
        kategorie = st.selectbox("Kategorie *", [
            "Zementhaltige Produkte", "Lösungsmittelhaltige Farben/Lacke/Kleber",
            "Epoxidharze (2-Komponenten)", "PU-Produkte (Isocyanate)",
            "Kraftstoffe & Schmiermittel", "Reinigungsmittel (Sauer)",
            "Chemikalie", "Baustoff", "Klebstoff", "Lack/Farbe", "Sonstiges",
        ])
        lagerort = st.text_input("Lagerort *")
        menge = st.text_input("Lagermenge *")
        cas_nummer = st.text_input("CAS-Nummer (optional)")
        ghs_symbole = st.text_input("GHS-Symbole")
        gefahrenbeschreibung = st.text_area("Gefahrenbeschreibung")
        schutzmassnahmen = st.text_area("Schutzmassnahmen")
        verwendung = st.text_input("Verwendung")
        betriebsanweisung = st.selectbox("Betriebsanweisung vorhanden?", ["Ja", "Nein"])
        substitution = st.text_area("Substitution (Ersatzpflicht)")
        sdb_link = st.text_input("Link zum Sicherheitsdatenblatt")

        if st.form_submit_button("Hinzufügen", type="primary", use_container_width=True):
            if not handelsbezeichnung or not hersteller or not lagerort or not menge:
                st.error("❌ Pflichtfelder ausfüllen!")
            else:
                add_gefahrstoff(
                    owner="all" if is_admin() else st.session_state.username,
                    name=handelsbezeichnung,
                    handelsbezeichnung=handelsbezeichnung,
                    hersteller=hersteller,
                    kategorie=kategorie,
                    lagerort=lagerort,
                    menge=menge,
                    cas_nummer=cas_nummer or "",
                    ghs_symbole=ghs_symbole or "",
                    gefahrenbeschreibung=gefahrenbeschreibung or "",
                    schutzmassnahmen=schutzmassnahmen or "",
                    verwendung=verwendung or "",
                    betriebsanweisung_vorhanden=betriebsanweisung,
                    substitution=substitution or "",
                    sdb_link=sdb_link or "",
                    sdb_datei="",
                    sdb_datum="",
                )
                st.success(f"✅ '{handelsbezeichnung}' hinzugefügt!")
                st.rerun()
