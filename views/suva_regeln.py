"""SUVA – 8 lebenswichtige Regeln"""
import os
import streamlit as st
from config import suva_regel_bild
from data import SUVA_REGELN


def render_suva():
    st.header("📋 Die 8 lebenswichtigen Regeln (SUVA)")
    st.info("ℹ️ **Quelle:** Basierend auf den lebenswichtigen Regeln der SUVA. "
            "Bilder, Grafiken und Texte: © SUVA. Dies ist keine offizielle SUVA-App.")
    st.markdown("---")

    for r in SUVA_REGELN:
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                bild = suva_regel_bild(r["bild_nr"])
                if os.path.exists(bild):
                    st.image(bild, use_container_width=True)
                    st.caption("📷 **Quelle: SUVA**")
                else:
                    st.info("🖼️ Bild fehlt")
            with c2:
                st.subheader(r["titel"])
                st.write(r["desc"])
                st.caption("📝 **Basierend auf den lebenswichtigen Regeln der SUVA**")

    st.markdown("---")
    st.markdown("**Hinweis:** Alle Materialien sind urheberrechtlich geschützt und Eigentum der SUVA. © SUVA")
