"""
SafeSite Drohne – Konfiguration
Alle Konstanten, Pfade und Styling an einem Ort.
"""

# ============================================================
# PFADE (alles im Root – gleich wie die alte App)
# ============================================================
LOGO_FILE = "logo.jpg"
TITELBILD_FILE = "titelbild.png"

def suva_regel_bild(nr: int) -> str:
    return f"regel_{nr}.png"

# JSON-Datenbank-Dateien
USER_DB = "users.json"
CUSTOMERS_DB = "customers.json"
GEFAHRSTOFF_DB = "gefahrstoffe.json"
NOTFALL_DB = "notfall.json"

# ============================================================
# API – Gemini-Modelle (Prioritätsreihenfolge)
# ============================================================
GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]


def get_api_key() -> str:
    """Holt den Google API Key aus Streamlit Secrets."""
    import streamlit as st
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        st.error("⚠️ API Key fehlt! Bitte unter Settings > Secrets den Key GOOGLE_API_KEY eintragen.")
        st.stop()


def get_anthropic_key() -> str:
    """Holt den Anthropic API Key aus Streamlit Secrets."""
    import streamlit as st
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return ""  # Optional – App läuft auch ohne Claude


# Claude-Modell für Dual-AI-Verification
CLAUDE_MODEL = "claude-opus-4-20250514"

# ============================================================
# STYLING
# ============================================================
APP_CSS = """
<style>
    .stAppDeployButton {display: none;}
    footer {visibility: hidden;}
    [data-testid="stSidebarCollapsedControl"] {color: #FF6600 !important;}
    h1, h2, h3 { color: #FF6600 !important; }
</style>
"""

# ============================================================
# SEITEN-MAPPING
# ============================================================
PAGES = {
    "home":        "🏠 Startseite",
    "safesite":    "🔍 SafeSite-Check",
    "suva":        "📋 SUVA Regeln",
    "bauav":       "⚖️ BauAV",
    "notfall":     "🚨 Notfallmanagement",
    "gefahrstoff": "🧪 Gefahrstoffkataster",
    "wetter":      "🌤️ Wetter-Warnungen",
    "preise":      "💎 Preise",
}
