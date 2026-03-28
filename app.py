"""
SafeSite Drohne – Hauptanwendung
================================
Einstiegspunkt für Streamlit. Enthält nur:
  - Page Config
  - Session Init
  - Sidebar (Navigation + Login)
  - Routing zu den einzelnen Seiten

Gesamte Logik lebt in den Modulen:
  config.py   – Konstanten & Pfade
  auth.py     – Passwort-Hashing & Session
  db.py       – Datenzugriff (JSON → später Supabase)
  ai_engine.py – Gemini API
  reports.py  – PDF/Word Erstellung
  utils.py    – Hilfsfunktionen
  data.py     – Statische Daten (BauAV, SUVA)
  views/      – Einzelne Seiten
"""
import os
import streamlit as st

from config import LOGO_FILE, APP_CSS, PAGES
from auth import init_session, is_admin, login_user, logout_user
from db import check_login, find_customer, get_credits, migrate_legacy_data

# ============================================================
# 1. PAGE CONFIG (muss als erstes kommen)
# ============================================================
st.set_page_config(
    page_title="SafeSite Drohne",
    page_icon="logo.jpg" if os.path.exists("logo.jpg") else "🚁",
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# 2. INIT
# ============================================================
st.markdown(APP_CSS, unsafe_allow_html=True)
init_session()

# Einmalige Migration alter Daten
if "migration_done" not in st.session_state:
    migrate_legacy_data()
    st.session_state.migration_done = True

# ============================================================
# 3. SIDEBAR
# ============================================================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)

    st.markdown("")

    # Navigation aufbauen
    page_list = list(PAGES.values())
    page_keys = list(PAGES.keys())

    # Profil (wenn eingeloggt)
    if st.session_state.logged_in:
        page_keys.append("profil")
        page_list.append("👤 Mein Profil")

    # Admin: Kundenverwaltung
    if is_admin():
        page_keys.append("kunden")
        page_list.append("👥 Kundenverwaltung")

    # Aktuelle Seite finden
    try:
        current_idx = page_keys.index(st.session_state.current_page)
    except ValueError:
        current_idx = 0
        st.session_state.current_page = "home"

    selected = st.radio("Navigation", page_list, index=current_idx, label_visibility="collapsed")

    # Ausgewählte Seite setzen
    for key, label in zip(page_keys, page_list):
        if selected == label:
            st.session_state.current_page = key
            break

    st.divider()

    # === LOGIN / LOGOUT ===
    if not st.session_state.logged_in:
        st.markdown("##### 🔐 Login")
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Username / Email", label_visibility="collapsed", placeholder="Username / Email")
            p = st.text_input("Passwort", type="password", label_visibility="collapsed", placeholder="Passwort")

            if st.form_submit_button("Einloggen", use_container_width=True, type="primary"):
                # Direkt prüfen
                if check_login(u, p):
                    login_user(u)
                    st.rerun()
                else:
                    # Vielleicht hat der Kunde einen anderen Login-Key
                    kid, kdata = find_customer(u)
                    if kdata:
                        for key in [kdata.get("email", ""), kdata.get("username", "")]:
                            if key and check_login(key, p):
                                login_user(key)
                                st.rerun()
                    st.error("❌ Falscher Login!")
    else:
        st.markdown(f"##### ✅ {st.session_state.username}")

        if not is_admin() and st.session_state.username:
            credits = get_credits(st.session_state.username)
            st.metric("🪙 Credits", credits)

        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()

    # Sidebar Footer
    st.markdown("")
    st.markdown("")
    st.markdown(
        '<div style="text-align:center; font-size:10px; color:#666; padding-top:20px;">'
        'SafeSite Drohne v2.0<br>'
        'Dual-AI-Verification'
        '</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 4. ROUTING
# ============================================================
from views import (
    render_home, render_check, render_suva, render_bauav,
    render_notfall, render_gefahrstoff, render_wetter,
    render_preise, render_profil, render_kunden,
)

ROUTER = {
    "home": render_home,
    "safesite": render_check,
    "suva": render_suva,
    "bauav": render_bauav,
    "notfall": render_notfall,
    "gefahrstoff": render_gefahrstoff,
    "wetter": render_wetter,
    "preise": render_preise,
    "profil": render_profil,
    "kunden": render_kunden,
}

page_func = ROUTER.get(st.session_state.current_page, render_home)
page_func()
