"""
SafeSite Drohne – Authentifizierung
Passwort-Hashing mit PBKDF2, Login/Logout-Logik.
"""
import hashlib
import os
import streamlit as st


# ============================================================
# PASSWORT-HASHING (PBKDF2-SHA256)
# ============================================================
_ITERATIONS = 100_000

def hash_password(password: str) -> str:
    """Erstellt einen sicheren Hash aus einem Passwort."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Prüft ein Passwort gegen den gespeicherten Hash.
    Unterstützt auch alte Klartext-Passwörter (Migration).
    """
    if ":" not in stored:
        # Alt: Klartext – direkter Vergleich
        return password == stored
    salt_hex, key_hex = stored.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return key.hex() == key_hex


def needs_rehash(stored: str) -> bool:
    """True wenn das Passwort noch im Klartext gespeichert ist."""
    return ":" not in stored


# ============================================================
# SESSION-MANAGEMENT
# ============================================================
def init_session():
    """Initialisiert alle Session-State-Variablen."""
    defaults = {
        "logged_in": False,
        "username": None,
        "current_page": "home",
        "app_step": "upload",       # upload → analyse → bericht
        "analysis_data": [],
        "m_type": None,
        "m_files": [],
        "confirmed": [],
        "meta_p": "",
        "meta_i": "",
        "meta_s": "",
        "pdf_file_path": None,
        "word_file_path": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def is_admin() -> bool:
    return st.session_state.logged_in and st.session_state.username == "admin"


def login_user(username: str):
    """Setzt Session-State nach erfolgreichem Login."""
    st.session_state.logged_in = True
    st.session_state.username = username


def logout_user():
    """Setzt Session-State auf Ausgangszustand."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.current_page = "home"
    st.session_state.app_step = "upload"
    st.session_state.analysis_data = []
    st.session_state.m_files = []
    st.session_state.confirmed = []
    st.session_state.pdf_file_path = None
    st.session_state.word_file_path = None


def reset_check():
    """Setzt den SafeSite-Check auf Anfang zurück."""
    st.session_state.app_step = "upload"
    st.session_state.analysis_data = []
    st.session_state.m_files = []
    st.session_state.confirmed = []
    st.session_state.pdf_file_path = None
    st.session_state.word_file_path = None
