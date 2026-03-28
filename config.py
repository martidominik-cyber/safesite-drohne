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
    /* === GLOBAL === */
    .stAppDeployButton {display: none;}
    footer {visibility: hidden;}
    [data-testid="stSidebarCollapsedControl"] {color: #FF6600 !important;}

    /* === TYPOGRAFIE === */
    h1 { color: #1a1a1a !important; font-weight: 700 !important; }
    h2 { color: #FF6600 !important; font-weight: 600 !important; }
    h3 { color: #333 !important; font-weight: 600 !important; }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 6px 12px !important;
        border-radius: 8px !important;
        transition: background 0.2s !important;
        margin-bottom: 2px !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 102, 0, 0.15) !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] input[type="radio"]:checked + div {
        color: #FF6600 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: #FF6600 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #e55b00 !important;
    }

    /* === FEATURE CARDS (Startseite) === */
    .feature-card {
        background: white;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .feature-card:hover {
        border-color: #FF6600;
        box-shadow: 0 4px 20px rgba(255, 102, 0, 0.15);
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 36px;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 16px;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 6px;
    }
    .feature-desc {
        font-size: 13px;
        color: #666;
        line-height: 1.4;
    }

    /* === HERO SECTION === */
    .hero-badge {
        display: inline-block;
        background: rgba(255, 102, 0, 0.1);
        color: #FF6600;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    .hero-title {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #1a1a1a !important;
        line-height: 1.2 !important;
        margin-bottom: 8px !important;
    }
    .hero-subtitle {
        font-size: 18px;
        color: #666;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    /* === STAT COUNTER === */
    .stat-box {
        text-align: center;
        padding: 16px;
    }
    .stat-number {
        font-size: 32px;
        font-weight: 800;
        color: #FF6600;
    }
    .stat-label {
        font-size: 13px;
        color: #888;
        margin-top: 4px;
    }

    /* === TRUST BAR === */
    .trust-bar {
        background: #f8f8f8;
        border-radius: 12px;
        padding: 20px 24px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin: 24px 0;
    }
    .trust-item {
        text-align: center;
        font-size: 13px;
        color: #555;
    }
    .trust-icon {
        font-size: 22px;
        margin-bottom: 6px;
    }

    /* === ALLGEMEIN === */
    .stButton > button[kind="primary"] {
        background: #FF6600 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #e55b00 !important;
    }
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
