"""Wetter-Warnungen – MeteoSchweiz Integration"""
import streamlit as st


def render_wetter():
    st.header("🌤️ Wetter-Warnungen")
    st.markdown("**Direkte Schnittstelle zu MeteoSchweiz.**")
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 📊 Wettervorhersage")
            st.caption("Aktuelle Wetterkarte der Schweiz")
            st.link_button("🗺️ Karte öffnen",
                "https://www.meteoschweiz.admin.ch/#tab=forecast-map",
                use_container_width=True, type="primary")
    with c2:
        with st.container(border=True):
            st.markdown("### 🌪️ Gefahrenkarte")
            st.caption("Aktuelle Wetterwarnungen")
            st.link_button("⚠️ Warnungen öffnen",
                "https://www.meteoschweiz.admin.ch/service-und-publikationen/applikationen/gefahren.html",
                use_container_width=True, type="primary")

    st.info("💡 Installieren Sie die MeteoSwiss App für Push-Benachrichtigungen.")
    st.markdown("---")

    st.subheader("⚠️ Wichtige Warnungen für Baustellen")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 🌪️ Sturmwarnungen")
            st.markdown("**Kranbetrieb einstellen bei:**")
            st.markdown("🔴 Windgeschwindigkeit > 50 km/h (Bft 7)")
            st.markdown("🔴 Böen > 70 km/h")
            st.markdown("🔴 Warnung vor Sturm oder Orkan")
            st.error("⚠️ SOFORT: Kranbetrieb einstellen! Lasten sichern.")
    with c2:
        with st.container(border=True):
            st.markdown("### ☀️ Hitzewarnungen (SUVA)")
            st.markdown("🟡 > 30°C: Erhöhte Vorsicht")
            st.markdown("🟠 > 35°C: Zusätzliche Pausen")
            st.markdown("🔴 Hitzewelle: Arbeitszeiten anpassen")
            st.warning("⚠️ SUVA: Trinken, Schatten, Arbeitszeiten anpassen.")

    st.markdown("---")
    st.subheader("📋 Checkliste: Wetter-Check")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Vor Arbeitsbeginn:")
            for item in ["Wetterwarnungen abrufen", "Windgeschwindigkeit prüfen",
                         "Temperatur prüfen", "Niederschlag?", "Gewitterwarnung?"]:
                st.markdown(f"- ☐ {item}")
        with c2:
            st.markdown("#### Bei Warnungen:")
            for item in ["Baustellenleiter informieren", "Massnahmen umsetzen",
                         "Mitarbeiter informieren", "PSA anpassen", "Arbeitszeiten anpassen"]:
                st.markdown(f"- ☐ {item}")
