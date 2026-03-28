"""
SafeSite Drohne – Statische Daten
BauAV-Artikel, SUVA-Regeln
"""

# ============================================================
# SUVA – 8 lebenswichtige Regeln
# ============================================================
SUVA_REGELN = [
    {"titel": "1. Absturzkanten sichern", "desc": "Ab 2.0m Absturzhöhe sind Seitenschutz oder Auffangeinrichtungen zwingend.", "bild_nr": 1},
    {"titel": "2. Bodenöffnungen", "desc": "Jede Öffnung muss durchbruchsicher abgedeckt und fixiert sein.", "bild_nr": 2},
    {"titel": "3. Lasten anschlagen", "desc": "Lasten nur von instruiertem Personal anschlagen. Niemals unter schwebenden Lasten.", "bild_nr": 3},
    {"titel": "4. Fassadengerüste", "desc": "Ab 3.0m Absturzhöhe ist ein Fassadengerüst erforderlich.", "bild_nr": 4},
    {"titel": "5. Gerüstkontrolle", "desc": "Tägliche Sichtkontrolle durch den Benutzer. Beläge müssen dicht sein.", "bild_nr": 5},
    {"titel": "6. Sichere Zugänge", "desc": "Treppentürme sind Leitern vorzuziehen. Leitern gegen Wegrutschen sichern.", "bild_nr": 6},
    {"titel": "7. PSA tragen", "desc": "Helm und Sicherheitsschuhe sind Pflicht. Je nach Situation: Weste, Brille, Gehörschutz.", "bild_nr": 7},
    {"titel": "8. Gräben sichern", "desc": "Ab 1.50m Tiefe müssen Gräben gespriesst oder geböscht werden.", "bild_nr": 8},
]

# ============================================================
# BauAV – Artikel (gruppiert nach Kategorie)
# ============================================================
BAUAV_KATEGORIEN = [
    "Organisation & Grundlagen",
    "Absturzsicherung & Öffnungen",
    "Zugänge, Verkehrswege & Leitern",
    "Gerüste",
    "Tiefbau & Gräben",
    "Gesundheit & Spezielle Gefahren",
]

BAUAV_ARTIKEL = [
    # 1. Organisation & Grundlagen
    {"cat": 0, "nr": 3, "titel": "Planung und Organisation", "text": "Bauarbeiten müssen so geplant werden, dass das Risiko von Unfällen und Gesundheitsbeeinträchtigungen möglichst klein ist. Die Baustelle muss geordnet sein."},
    {"cat": 0, "nr": 4, "titel": "Kontrolle der Arbeitsmittel", "text": "Gerüste, Maschinen und Geräte müssen vor jedem Gebrauch auf Mängel geprüft werden. Defektes Material darf nicht verwendet werden."},
    {"cat": 0, "nr": 5, "titel": "Persönliche Schutzausrüstung (PSA)", "text": "Helmpflicht ist obligatorisch. Je nach Gefährdung sind Warnwesten, Sicherheitsschuhe, Gehörschutz oder Schutzbrillen zu tragen."},
    {"cat": 0, "nr": 6, "titel": "Verhalten bei Gefahr", "text": "Bei unmittelbarer Gefahr (z.B. drohender Einsturz, Unwetter) sind die Arbeiten sofort einzustellen und die Gefahrenzone zu verlassen."},
    {"cat": 0, "nr": 12, "titel": "Absperrung der Baustelle", "text": "Die Baustelle muss gegen unbefugtes Betreten gesichert sein. Zäune, Signale und Warnschilder sind erforderlich."},
    {"cat": 0, "nr": 22, "titel": "Ordnung auf der Baustelle", "text": "Materialien sind stabil zu lagern. Keine Gefährdung durch Umkippen oder Wegrollen. Arbeitsplätze müssen aufgeräumt sein."},

    # 2. Absturzsicherung & Öffnungen
    {"cat": 1, "nr": 17, "titel": "Absturzkanten (Allgemein)", "text": "Ab einer Absturzhöhe von 2.00 m ist ein Seitenschutz zwingend (Holm, Zwischenholm, Bordbrett). Die Höhe des Seitenschutzes muss mindestens 1.00 m betragen."},
    {"cat": 1, "nr": 25, "titel": "Bodenöffnungen", "text": "Löcher in Böden und Decken müssen durchbruchsicher abgedeckt und gegen Verschieben gesichert sein. Öffnungen sind deutlich zu kennzeichnen."},
    {"cat": 1, "nr": 41, "titel": "Arbeiten an Dächern", "text": "Ab 2.00 m Absturzhöhe müssen Dächer durch Fassadengerüste, Spenglerläufe oder Auffangnetze gesichert werden. Steildächer ab 30° Neigung zusätzlich mit Seilsicherung."},
    {"cat": 1, "nr": 19, "titel": "Herabfallende Gegenstände", "text": "Arbeitsbereiche, über denen gearbeitet wird, müssen gesichert sein (Schutzdächer oder Absperrungen). Werkzeuge müssen gegen Herunterfallen gesichert werden."},
    {"cat": 1, "nr": 18, "titel": "Schutz der Personen unterhalb", "text": "Wenn Arbeiten in Höhe ausgeführt werden, muss der Bereich darunter abgesperrt oder mit Schutzdächern gesichert sein."},

    # 3. Zugänge, Verkehrswege & Leitern
    {"cat": 2, "nr": 10, "titel": "Verkehrswege", "text": "Wege müssen frei von Hindernissen sein. Stolperstellen (Kabel, Material) sind zu entfernen. Wege müssen ausreichend breit und beleuchtet sein."},
    {"cat": 2, "nr": 15, "titel": "Zugänge zu Arbeitsplätzen", "text": "Zugänge müssen sicher sein. Treppentürme sind Leitern vorzuziehen. Steigungen dürfen nicht zu steil sein (max. 45°)."},
    {"cat": 2, "nr": 21, "titel": "Verwendung von Leitern", "text": "Leitern dürfen nur für kurzzeitige Arbeiten verwendet werden. Sie sind gegen Wegrutschen zu sichern. Niemals auf der obersten Sprosse stehen."},
    {"cat": 2, "nr": 34, "titel": "Leitern (Bauart)", "text": "Anlegeleitern müssen die Austrittsstelle um mindestens 1.00 m überragen. Der Neigungswinkel sollte zwischen 65° und 75° liegen."},
    {"cat": 2, "nr": 14, "titel": "Treppen und Rampen", "text": "Treppen müssen mindestens 0.80 m breit sein und Handläufe aufweisen. Rampen dürfen nicht steiler als 15° sein."},

    # 4. Gerüste
    {"cat": 3, "nr": 47, "titel": "Gerüste (Allgemein)", "text": "Gerüste müssen standfest sein. Der Belag muss lückenlos verlegt sein. Änderungen dürfen nur vom Gerüstbauer vorgenommen werden. Tägliche Sichtkontrolle ist erforderlich."},
    {"cat": 3, "nr": 57, "titel": "Rollgerüste", "text": "Rollgerüste dürfen nicht verschoben werden, solange sich Personen darauf befinden. Die Räder müssen arretiert sein. Maximale Höhe: 12 m."},
    {"cat": 3, "nr": 48, "titel": "Gerüstbeläge", "text": "Beläge müssen durchbruchsicher sein. Überlappungen müssen mindestens 20 cm betragen. Keine schadhaften Bretter verwenden."},
    {"cat": 3, "nr": 49, "titel": "Gerüstverankerung", "text": "Fassadengerüste müssen ausreichend verankert sein. Abstände der Verankerungen: alle 4 m in der Höhe, alle 6 m in der Breite."},
    {"cat": 3, "nr": 50, "titel": "Gerüstmontage", "text": "Gerüste dürfen nur von qualifiziertem Personal errichtet werden. Standsicherheitsnachweis ist erforderlich bei Gerüsten über 3 m Höhe."},

    # 5. Tiefbau & Gräben
    {"cat": 4, "nr": 20, "titel": "Gräben und Schächte", "text": "Ab einer Tiefe von 1.50 m müssen Grabenwände gespriesst oder geböscht werden. Bei fliessenden Böden schon früher. Verbau muss durchbruchsicher sein."},
    {"cat": 4, "nr": 82, "titel": "Arbeiten in der Nähe von Leitungen", "text": "Bei Grabarbeiten ist auf Werkleitungen (Gas, Strom, Wasser) zu achten. Pläne konsultieren! Mindestabstände beachten (Strom: 3-5 m je nach Spannung)."},
    {"cat": 4, "nr": 23, "titel": "Erdarbeiten", "text": "Böschungen müssen stabil sein. Neigung maximal 45° bei bindigen Böden, 35° bei nichtbindigen Böden. Maschinenabstände von Grabenkanten beachten (min. 0.5 m)."},
    {"cat": 4, "nr": 81, "titel": "Sprengarbeiten", "text": "Sprengarbeiten dürfen nur von qualifiziertem Personal ausgeführt werden. Sicherheitszone muss abgesperrt werden. Mindestabstand: 300 m."},

    # 6. Gesundheit & Spezielle Gefahren
    {"cat": 5, "nr": 32, "titel": "Schutz vor Sonne und Hitze", "text": "Arbeitsplätze sind wenn möglich zu beschatten. Genügend Trinkwasser bereitstellen. Pausen an kühlen Orten einplanen."},
    {"cat": 5, "nr": 33, "titel": "Staub, Lärm, Vibrationen", "text": "Gesundheitsgefährdende Einwirkungen minimieren (z.B. Wasser gegen Staub, Gehörschutz bei Lärm über 85 dB(A)). Vibrationen durch Dämpfung reduzieren."},
    {"cat": 5, "nr": 83, "titel": "Elektrische Freileitungen", "text": "Für Baumaschinen gelten Mindestabstände zu Freileitungen (Niederspannung 3 m / Hochspannung 5 m+)."},
    {"cat": 5, "nr": 24, "titel": "Brandverhütung", "text": "Brennbare Materialien sicher lagern. Feuerlöscher an gut zugänglichen Stellen. Rauchverbot auf Baustellen beachten."},
    {"cat": 5, "nr": 26, "titel": "Kranarbeiten", "text": "Krane müssen auf standsicherem Untergrund stehen. Ausleger nicht über Personen schwenken. Lasten sicher anschlagen."},
    {"cat": 5, "nr": 27, "titel": "Hebearbeiten", "text": "Lasten nur von instruiertem Personal anschlagen. Niemals unter schwebenden Lasten stehen."},
    {"cat": 5, "nr": 28, "titel": "Schweissarbeiten", "text": "Schweissplätze brandgeschützt einrichten. Brandwachen erforderlich. Gase getrennt lagern."},
    {"cat": 5, "nr": 29, "titel": "Umgang mit Chemikalien", "text": "Gefahrstoffe nach Sicherheitsdatenblatt handhaben. PSA entsprechend tragen. Behältnisse klar kennzeichnen."},
    {"cat": 5, "nr": 30, "titel": "Arbeitsplätze unter der Erde", "text": "Ausreichende Beleuchtung und Belüftung. Notausgänge kennzeichnen. Gasmessungen durchführen."},
    {"cat": 5, "nr": 31, "titel": "Lagerung von Materialien", "text": "Materialien stabil stapeln. Maximale Stapelhöhe beachten. Gänge freihalten (min. 0.8 m)."},
    {"cat": 5, "nr": 35, "titel": "Baumaschinen", "text": "Maschinen nur von qualifiziertem Personal bedienen. Tägliche Sichtkontrolle. Warntöne und Rückspiegel funktionsfähig."},
    {"cat": 5, "nr": 36, "titel": "Fahrzeuge auf der Baustelle", "text": "Höchstgeschwindigkeit 10 km/h. Fussgängerbereiche kennzeichnen. Tageslichtleuchten erforderlich."},
]
