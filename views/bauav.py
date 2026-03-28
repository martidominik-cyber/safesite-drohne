"""BauAV – Bauarbeitenverordnung Nachschlagewerk"""
import streamlit as st
from data import BAUAV_ARTIKEL, BAUAV_KATEGORIEN


def render_bauav():
    st.header("⚖️ Bauarbeitenverordnung (BauAV)")
    st.markdown("**Nachschlagewerk für die wichtigsten Artikel der Schweizer Bauarbeitenverordnung**")
    st.markdown("---")

    query = st.text_input("🔍 Suche in BauAV", placeholder="z.B. Gerüst, Absturz, Leiter...")
    st.markdown("---")

    # Filtern
    if query:
        q = query.lower()
        filtered = [a for a in BAUAV_ARTIKEL
                    if q in str(a["nr"]).lower()
                    or q in a["titel"].lower()
                    or q in a["text"].lower()]
        if filtered:
            st.success(f"✅ {len(filtered)} Artikel gefunden für '{query}'")
        else:
            st.warning(f"⚠️ Keine Artikel gefunden für '{query}'.")
            st.info("💡 Versuchen Sie: Gerüst, Absturz, Leiter, Gräben, PSA...")
            return
    else:
        filtered = BAUAV_ARTIKEL

    # Nach Kategorien gruppiert anzeigen
    current_cat = None
    for art in filtered:
        if art["cat"] != current_cat:
            if current_cat is not None:
                st.divider()
            cat_name = BAUAV_KATEGORIEN[art["cat"]] if art["cat"] < len(BAUAV_KATEGORIEN) else "Sonstige"
            st.markdown(f"### {art['cat']+1}. {cat_name}")
            current_cat = art["cat"]

        with st.expander(f"Art. {art['nr']} – {art['titel']}"):
            st.write(art["text"])
