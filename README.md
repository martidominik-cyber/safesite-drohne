# SafeSite Drohne v2

## Anleitung: So lädst du die neuen Dateien hoch

### Was du NICHT machen musst:
- ❌ Nichts löschen
- ❌ Nichts verschieben
- ❌ Keine Bilder anfassen

### Was du machen musst (3 Schritte):

**Schritt 1:** Auf GitHub diese Dateien HOCHLADEN (einfach dazu):
- `config.py`
- `auth.py`
- `db.py`
- `ai_engine.py`
- `reports.py`
- `utils.py`
- `data.py`
- `streamlit_app.py`
- `requirements.txt` (überschreibt die alte)

**Schritt 2:** Ordner `views/` erstellen und dort alle 11 Dateien hochladen:
- `__init__.py`
- `home.py`
- `check.py`
- `suva_regeln.py`
- `bauav.py`
- `notfall.py`
- `gefahrstoff.py`
- `wetter.py`
- `preise.py`
- `profil.py`
- `kunden.py`

**Schritt 3:** In Streamlit Cloud → Settings:
- Main file path ändern auf: `streamlit_app.py`
- Speichern → App deployed automatisch neu

### Fertig!
Die alte `app.py` bleibt einfach liegen und wird ignoriert.
