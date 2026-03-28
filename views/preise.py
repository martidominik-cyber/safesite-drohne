"""Preise – Flight Credits & Pakete"""
import urllib.parse
import streamlit as st


def render_preise():
    st.header("💎 Flight Credits & Pakete")

    st.markdown("""
    <style>
    .paket-card {
        border: 2px solid #f0e6e0; border-radius: 12px; padding: 20px;
        margin-bottom: 25px; background-color: #fdfaf6; position: relative;
    }
    .paket-card-beliebt { border: 2px solid #2da68e; background-color: #f6fbfa; }
    .paket-title { font-size: 22px; font-weight: 700; margin-bottom: 0px; }
    .paket-price { font-size: 24px; font-weight: 800; text-align: right; color: #333; }
    .paket-desc { color: #888; font-size: 14px; margin-top: -2px; margin-bottom: 15px; }
    .paket-feature { font-size: 15px; margin-bottom: 8px; color: #444; }
    .beliebt-badge {
        background-color: #2da68e; color: white; padding: 4px 10px;
        border-radius: 5px; font-size: 11px; font-weight: bold;
        position: absolute; top: -12px; right: 15px; text-transform: uppercase;
    }
    .paket-btn {
        display: block; width: 100%; text-align: center; color: white !important;
        padding: 12px; border-radius: 8px; text-decoration: none;
        font-weight: bold; font-size: 16px; margin-top: 5px; transition: opacity 0.2s;
    }
    .paket-btn:hover { opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

    pakete = [
        ("Paket S", "Der Einsteiger", "490 CHF/Monat", "5", "98.00 CHF", "#4eb0f5"),
        ("Paket M", "Der Standard", "1'800 CHF/Monat", "20", "90.00 CHF", "#2da68e"),
        ("Paket L", "Der Profi", "3'900 CHF/Monat", "50", "78.00 CHF", "#5b6bba"),
        ("Paket XL", "Enterprise / Konzern", "12'000 CHF/Monat", "200", "60.00 CHF", "#8359b8"),
    ]

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        for title, subtitle, price, credits, ppc, color in pakete:
            subject = urllib.parse.quote(f"Anfrage: {title}")
            body = urllib.parse.quote(
                f"Grüezi,\\n\\nich interessiere mich für das {title} ({price}).\\n\\n"
                f"Freundliche Grüsse\\n[Ihr Name]"
            )
            st.markdown(f"""
            <div class="paket-card paket-card-beliebt">
                <div class="beliebt-badge">Beliebt</div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div style="color:{color};" class="paket-title">{title}</div>
                    <div class="paket-price">{price}</div>
                </div>
                <div class="paket-desc">{subtitle}</div>
                <hr style="margin:15px 0;border:0;border-top:1px solid #eee;">
                <div class="paket-feature">
                    <span style="color:#4caf50;font-weight:bold;margin-right:5px;">✓</span>
                    {credits} Flüge (Credits)
                </div>
                <div class="paket-feature">
                    <span style="color:#2196f3;margin-right:5px;">📄</span>
                    Preis pro Flug: {ppc}
                </div>
                <a href="mailto:info@safesite-drohne.ch?subject={subject}&body={body}"
                   class="paket-btn" style="background-color:{color};">
                    Paket anfragen
                </a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            "<p style='text-align:center;color:#888;font-size:12px;margin-top:20px;'>"
            "Alle Preise exkl. MwSt. Weitere Konditionen auf Anfrage.</p>",
            unsafe_allow_html=True,
        )
