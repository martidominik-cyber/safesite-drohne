"""
SafeSite Drohne – Statische Daten
BauAV SR 832.311.141 (Stand 1. Januar 2024) – ALLE Artikel
SUVA – 8 lebenswichtige Regeln
"""

# ============================================================
# SUVA – 8 lebenswichtige Regeln
# ============================================================
SUVA_REGELN = [
    {"titel": "1. Absturzkanten sichern", "desc": "Ab 2.0 m Absturzhöhe sind Seitenschutz oder Auffangeinrichtungen zwingend.", "bild_nr": 1},
    {"titel": "2. Bodenöffnungen", "desc": "Jede Öffnung muss durchbruchsicher abgedeckt und fixiert sein.", "bild_nr": 2},
    {"titel": "3. Lasten anschlagen", "desc": "Lasten nur von instruiertem Personal anschlagen. Niemals unter schwebenden Lasten.", "bild_nr": 3},
    {"titel": "4. Fassadengerüste", "desc": "Ab 3.0 m Absturzhöhe ist ein Fassadengerüst erforderlich.", "bild_nr": 4},
    {"titel": "5. Gerüstkontrolle", "desc": "Tägliche Sichtkontrolle durch den Benutzer. Beläge müssen dicht sein.", "bild_nr": 5},
    {"titel": "6. Sichere Zugänge", "desc": "Treppentürme sind Leitern vorzuziehen. Leitern gegen Wegrutschen sichern.", "bild_nr": 6},
    {"titel": "7. PSA tragen", "desc": "Helm und Sicherheitsschuhe sind Pflicht. Je nach Situation: Weste, Brille, Gehörschutz.", "bild_nr": 7},
    {"titel": "8. Gräben sichern", "desc": "Ab 1.50 m Tiefe müssen Gräben gespriesst oder geböscht werden.", "bild_nr": 8},
]

# ============================================================
# BauAV SR 832.311.141 – Kategorien (Kapitel/Abschnitte)
# ============================================================
BAUAV_KATEGORIEN = [
    "1. Kapitel: Allgemeine Bestimmungen",                          # 0
    "2. Kapitel / 1. Abschnitt: Allgemeines",                       # 1
    "2. Kapitel / 2. Abschnitt: Arbeitsplätze und Verkehrswege",    # 2
    "2. Kapitel / 3. Abschnitt: Leitern",                           # 3
    "2. Kapitel / 4. Abschnitt: Absturzsicherungen",                # 4
    "2. Kapitel / 5. Abschnitt: Bestehende Anlagen & Energie",      # 5
    "2. Kapitel / 6. Abschnitt: Arbeitsumgebung",                   # 6
    "2. Kapitel / 7. Abschnitt: Transport",                         # 7
    "3. Kapitel: Arbeiten auf Dächern",                              # 8
    "4. Kapitel: Gerüste – Allgemeine Bestimmungen",                 # 9
    "4. Kapitel: Arbeitsgerüste",                                    # 10
    "4. Kapitel: Fanggerüste und Auffangnetze",                      # 11
    "5. Kapitel: Gräben, Schächte und Baugruben",                    # 12
    "6. Kapitel: Rückbau- und Abbrucharbeiten",                      # 13
    "7. Kapitel: Untertagarbeiten",                                  # 14
    "8. Kapitel: Abbau von Gestein, Kies und Sand",                  # 15
    "9. Kapitel: Wärmetechnische Anlagen und Hochkamine",            # 16
    "10. Kapitel: Arbeiten am hängenden Seil",                       # 17
    "11. Kapitel: Arbeiten in Rohrleitungen",                        # 18
]

# ============================================================
# BauAV – ALLE Artikel (Art. 1–124)
# ============================================================
BAUAV_ARTIKEL = [
    # ==========================================================
    # 1. KAPITEL: ALLGEMEINE BESTIMMUNGEN (Art. 1–2)
    # ==========================================================
    {"cat": 0, "nr": 1, "titel": "Gegenstand",
     "text": "Diese Verordnung legt die Massnahmen fest, die für die Sicherheit und den Gesundheitsschutz der Arbeitnehmerinnen und Arbeitnehmer bei Bauarbeiten getroffen werden müssen."},

    {"cat": 0, "nr": 2, "titel": "Begriffe",
     "text": "Bauarbeiten: Erstellung, Instandstellung, Änderung, Unterhalt, Kontrolle, Rückbau und Abbruch von Bauwerken. Absturzhöhe: Bei Neigung bis 60° die Höhendifferenz zwischen Absturzkante und tiefstmöglicher Aufschlagstelle; bei Neigung über 60° die Höhendifferenz zwischen höchstmöglichem Absturzbeginn und tiefstmöglicher Aufschlagstelle. Durchbruchsichere Fläche: Fläche, die allen Belastungen standhält, die während der Ausführung von Arbeiten auftreten können."},

    # ==========================================================
    # 2. KAPITEL / 1. ABSCHNITT: ALLGEMEINES (Art. 3–8)
    # ==========================================================
    {"cat": 1, "nr": 3, "titel": "Planung von Bauarbeiten",
     "text": "Bauarbeiten müssen so geplant werden, dass das Risiko von Berufsunfällen, Berufskrankheiten oder Gesundheitsbeeinträchtigungen möglichst klein ist. Bei Verdacht auf besonders gesundheitsgefährdende Stoffe (Asbest, PCB) ist die Gefährdung eingehend zu ermitteln. Der Arbeitgeber hat vor Vertragsabschluss zu prüfen, welche Massnahmen nötig sind. Geeignete Materialien und Geräte müssen in genügender Menge und rechtzeitig zur Verfügung stehen."},

    {"cat": 1, "nr": 4, "titel": "Sicherheits- und Gesundheitsschutzkonzept",
     "text": "Vor Beginn der Bauarbeiten muss ein Konzept vorliegen, in dem die erforderlichen Sicherheits- und Gesundheitsschutzmassnahmen aufgezeigt werden. Das Konzept muss namentlich die Notfallorganisation regeln. Es muss schriftlich erstellt werden."},

    {"cat": 1, "nr": 5, "titel": "Organisation der Arbeitssicherheit und des Gesundheitsschutzes",
     "text": "Der Arbeitgeber muss auf jeder Baustelle eine Person bezeichnen, die für Arbeitssicherheit und Gesundheitsschutz zuständig ist. Diese Person muss den Arbeitnehmern Weisungen erteilen können. Wer sich selbst oder andere gefährdet, ist von der Baustelle wegzuweisen."},

    {"cat": 1, "nr": 6, "titel": "Schutzhelmtragpflicht",
     "text": "Ein Schutzhelm ist zu tragen bei allen Arbeiten mit Gefährdung durch herunterfallende Gegenstände. In jedem Fall bei: a) Hochbau-/Brückenbau bis Rohbauabschluss, b) im Bereich von Kranen/Aushubgeräten, c) Graben-/Schachtbau/Baugruben, d) Steinbrüchen, e) Untertagarbeiten, f) Sprengarbeiten, g) Rückbau/Abbruch, h) Gerüstbauarbeiten, i) Arbeiten an/in Rohrleitungen. Schutzhelm MIT Kinnband bei: Seilsicherung (PSAgA), Arbeiten am hängenden Seil, Arbeiten im Bereich von Helikoptern."},

    {"cat": 1, "nr": 7, "titel": "Warnkleider",
     "text": "Bei Arbeiten im Bereich von Baumaschinen, Transportfahrzeugen oder öffentlichen Verkehrswegen müssen Warnkleider in farbigem fluoreszierendem Material höchster Auffälligkeit mit retroreflektierenden Flächen getragen werden."},

    {"cat": 1, "nr": 8, "titel": "Rettung von Verunfallten",
     "text": "Es muss gewährleistet sein, dass Verunfallte gerettet werden können. Den Arbeitnehmern sind die Notrufnummern der Rettungsdienste (Arzt, Spital, Ambulanz, Polizei, Feuerwehr, Helikopter) in geeigneter Form bekannt zu geben."},

    # ==========================================================
    # 2. KAPITEL / 2. ABSCHNITT: ARBEITSPLÄTZE & VERKEHRSWEGE (Art. 9–19)
    # ==========================================================
    {"cat": 2, "nr": 9, "titel": "Allgemeine Anforderungen",
     "text": "Die Arbeitsplätze müssen sicher und über sichere Verkehrswege erreichbar sein. Zur Gewährleistung der Sicherheit sind Absturzsicherungen nach Art. 22–29 anzubringen."},

    {"cat": 2, "nr": 10, "titel": "Entfernung von scharfkantigen und spitzigen Gegenständen",
     "text": "Scharfkantige und spitzige Gegenstände sind zu entfernen oder abzudecken. Vorstehende Armierungsstäbe müssen mit Haken ausgebildet sein. Ist dies nicht möglich, ist die Verletzungsgefahr durch geeignete Abdeckungen auszuschliessen."},

    {"cat": 2, "nr": 11, "titel": "Verkehrswege",
     "text": "a) Baustellenzugänge mind. 1 m breit, übrige Verkehrswege mind. 60 cm. b) Verkehrswege sind freizuhalten. c) Bei Gleitgefahr: geeignete Massnahmen, insbesondere Schnee und Eis entfernen. d) Bei Steigungen über 10°: Rutschsicherung. e) An Treppen mit mehr als 5 Stufen: Handlauf; bei Absturzseite: Seitenschutz statt Handlauf."},

    {"cat": 2, "nr": 12, "titel": "Nicht durchbruchsichere Flächen, Bauteile und Abdeckungen",
     "text": "Bei nicht durchbruchsicheren Flächen sind Abschrankungen anzubringen oder Massnahmen zu treffen, damit sie nicht versehentlich begangen werden. Verkehrswege darüber sind über Laufstege mit beidseitigem Seitenschutz zu führen. An den Zugängen sind Anschlagtafeln anzubringen."},

    {"cat": 2, "nr": 13, "titel": "Laufstege und Abdeckungen",
     "text": "Laufstege und Abdeckungen müssen eine ihrer Funktion entsprechende Grösse und Stärke aufweisen sowie gegen Verrutschen gesichert sein."},

    {"cat": 2, "nr": 14, "titel": "Durchgang bei sich bewegenden Anlageteilen",
     "text": "Zwischen sich bewegenden Anlageteilen und festen Hindernissen ist ein freier Durchgang von 0,5 m Breite und 2,5 m Höhe freizuhalten. Wird eines unterschritten, ist der Durchgang zu sperren oder die Anlageteile zu verschalen."},

    {"cat": 2, "nr": 15, "titel": "Zugang bei Niveauunterschieden",
     "text": "Sind zum Erreichen der Arbeitsplätze Niveauunterschiede von mehr als 50 cm zu überwinden, so sind Treppen oder andere geeignete Arbeitsmittel zu verwenden."},

    {"cat": 2, "nr": 16, "titel": "Fahrbahnen",
     "text": "Fahrbahnen müssen den zu erwartenden Lasten standhalten. Bei Kunstbauten (Brücken, Dämme) muss ein Tragfähigkeitsnachweis vorliegen. An Fahrbahnen mit Absturzgefahr sind Leitplanken oder Radabweiser zu montieren. Abstand Fahrspurrand zu Dammrand mind. 1 m."},

    {"cat": 2, "nr": 17, "titel": "Schutz vor einstürzenden Bauteilen und herabfallenden Gegenständen",
     "text": "Bei Arbeitsplätzen und Verkehrswegen sind Massnahmen zu treffen, damit Arbeitnehmer nicht durch einstürzende Bauteile oder herabfallende, herabgleitende, herabrollende oder herabfliessende Gegenstände oder Materialien gefährdet werden."},

    {"cat": 2, "nr": 18, "titel": "Werfen oder Fallenlassen von Gegenständen und Materialien",
     "text": "Gegenstände und Materialien dürfen nur geworfen oder fallen gelassen werden, wenn der Zugang zum Gefahrenbereich abgesperrt ist oder wenn sie über Kanäle, geschlossene Rutschen oder Ähnliches geführt werden."},

    {"cat": 2, "nr": 19, "titel": "Fahrten von Transportfahrzeugen und Baumaschinen",
     "text": "Es ist sicherzustellen, dass sich keine Personen im Gefahrenbereich aufhalten. Falls doch nötig: technische Massnahmen (Kameras, Spiegel) oder Überwachung durch Hilfsperson. Rückwärtsfahrten sind so kurz wie möglich zu halten."},

    # ==========================================================
    # 2. KAPITEL / 3. ABSCHNITT: LEITERN (Art. 20–21)
    # ==========================================================
    {"cat": 3, "nr": 20, "titel": "Anforderungen an Leitern",
     "text": "Nur Leitern verwenden, die bezüglich Belastbarkeit und Standfestigkeit geeignet und unbeschädigt sind. Leitern müssen auf tragfähiger Unterlage stehen und gegen Wegrutschen, Drehen und Kippen gesichert sein. Standort so wählen, dass keine Gefahr durch herabfallende Gegenstände besteht. Anstellleitern: oberste 3 Sprossen nur mit Plattform und Haltevorrichtung besteigen. Bockleitern: oberste 2 Sprossen nicht besteigen, nur vom Leiterfuss her begehen."},

    {"cat": 3, "nr": 21, "titel": "Arbeiten von tragbaren Leitern aus",
     "text": "Von tragbaren Leitern aus dürfen Arbeiten nur ausgeführt werden, wenn kein anderes Arbeitsmittel besser geeignet ist. Ab Absturzhöhe über 2 m: nur von kurzer Dauer und mit Absturzsicherungsmassnahmen."},

    # ==========================================================
    # 2. KAPITEL / 4. ABSCHNITT: ABSTURZSICHERUNGEN (Art. 22–29)
    # ==========================================================
    {"cat": 4, "nr": 22, "titel": "Anforderungen an den Seitenschutz",
     "text": "Ein Seitenschutz besteht aus: Geländerholm, mindestens einem Zwischenholm und einem Bordbrett. Oberkante Geländerholm: mind. 100 cm über Standfläche. Bordbrett: mind. 15 cm Höhe ab Standfläche. Abstand zwischen Holmen und Bordbrett: max. 47 cm. Alternativ Rahmen/Gitter mit max. 25 cm Maschenweite. Seitenschutz ist so zu befestigen, dass er nicht unbeabsichtigt entfernt werden kann."},

    {"cat": 4, "nr": 23, "titel": "Verwendung des Seitenschutzes",
     "text": "Seitenschutz ist zu verwenden bei: a) Absturzhöhe über 2 m, b) Böschungen über 2 m Höhe und Neigung über 45°, c) im Bereich von Gewässern. Bei Verkehrswegen an Gewässern/Böschungen genügt ein Geländerholm. Bei Gräben für Werkleitungen kann verzichtet werden, wenn sich niemand am Grabenrand aufhalten muss."},

    {"cat": 4, "nr": 24, "titel": "Niveauunterschiede bei Böden",
     "text": "Im Gebäudeinnern sind bei Böden Niveauunterschiede von mehr als 50 cm mit einem Geländerholm abzuschranken."},

    {"cat": 4, "nr": 25, "titel": "Bodenöffnungen",
     "text": "Bodenöffnungen, bei denen die Gefahr besteht, dass man hineinfällt oder hineintritt, sind mit einem Seitenschutz abzuschranken oder mit einer durchbruchsicheren und unverrückbaren Abdeckung zu versehen."},

    {"cat": 4, "nr": 26, "titel": "Fassadengerüste bei Hochbauarbeiten",
     "text": "Ab Absturzhöhe über 3 m ist ein Fassadengerüst zu erstellen. Der oberste Holm muss die höchste Absturzkante um mind. 80 cm überragen, oder um mind. 100 cm wenn der Seitenschutz näher als 60 cm zur Absturzkante liegt."},

    {"cat": 4, "nr": 27, "titel": "Auffangnetz und Fanggerüst für vorgefertigte Dach-/Deckenelemente",
     "text": "Für die Montage von vorgefertigten Dach- und Deckenelementen sind ab Absturzhöhe über 3 m über die ganze Fläche Auffangnetze oder Fanggerüste zu verwenden. Tägliche Sichtkontrolle. Bei Mängeln: keine Arbeiten."},

    {"cat": 4, "nr": 28, "titel": "Betreten von vorgefertigten Dach- und Deckenelementen",
     "text": "Vorgefertigte Dach- und Deckenelemente dürfen erst betreten werden, wenn sie befestigt sind."},

    {"cat": 4, "nr": 29, "titel": "Andere Absturzsicherungen",
     "text": "Wo Seitenschutz (Art. 22), Fassadengerüst (Art. 26) oder Auffangnetz/Fanggerüst (Art. 27) technisch nicht möglich oder zu gefährlich ist, sind gleichwertige Schutzmassnahmen zu treffen. Diese müssen unter Beizug eines Spezialisten für Arbeitssicherheit schriftlich festgelegt werden."},

    # ==========================================================
    # 2. KAPITEL / 5. ABSCHNITT: BESTEHENDE ANLAGEN & ENERGIE (Art. 30–31)
    # ==========================================================
    {"cat": 5, "nr": 30, "titel": "Bestehende Anlagen",
     "text": "Vor Beginn der Bauarbeiten muss abgeklärt werden, ob im Arbeitsbereich Anlagen vorhanden sind (elektrische Anlagen, Verkehrsanlagen, Leitungen, Kanäle, Schächte, Anlagen mit Explosionsgefahr). Mit den Eigentümern ist schriftlich festzulegen, welche Sicherheitsmassnahmen erforderlich sind. Werden Anlagen erst nach Arbeitsaufnahme entdeckt: Arbeiten einstellen, Bauherrschaft benachrichtigen."},

    {"cat": 5, "nr": 31, "titel": "Energieversorgung auf Baustellen",
     "text": "Gesetzliche Vorschriften und anerkannte Regeln der Technik beachten. Steckdosen bis 32 A: Fehlerstromschutzschaltung (FI) mit max. 30 mA Nennauslösestrom obligatorisch. Steckdosen über 32 A: ebenfalls durch Fehlerstromschutzeinrichtungen geschützt."},

    # ==========================================================
    # 2. KAPITEL / 6. ABSCHNITT: ARBEITSUMGEBUNG (Art. 32–39)
    # ==========================================================
    {"cat": 6, "nr": 32, "titel": "Besonders gesundheitsgefährdende Stoffe",
     "text": "Bei Verdacht auf Asbest oder PCB: Massnahmen nach Art. 3 Abs. 2 treffen. Arbeitnehmer über Ergebnis von Schadstoffgutachten informieren. Wird ein gefährlicher Stoff unerwartet vorgefunden: betroffene Arbeiten einstellen, Bauherrschaft benachrichtigen."},

    {"cat": 6, "nr": 33, "titel": "Luftqualität",
     "text": "Sauerstoffgehalt am Arbeitsplatz: 19–21 Vol%. Grenzwerte für gesundheitsgefährdende Stoffe (MAK-Werte) dürfen nicht überschritten werden. Gefährliche Stoffe ins Freie ableiten, filtern oder durch künstliche Lüftung verdünnen. Krebserzeugende Stoffe müssen ins Freie abgeleitet werden. Luftqualität regelmässig prüfen. Falls nötig: Atemschutzgeräte."},

    {"cat": 6, "nr": 34, "titel": "Explosions- und Brandgefahr",
     "text": "Geeignete Massnahmen zur Verhütung von Explosionen und Bränden treffen. Arbeitsplätze müssen im Brandfall gefahrlos verlassen werden können. Löschmittel in unmittelbarer Nähe. Explosionsgefährdete Bereiche absperren und mit Warndreieck kennzeichnen."},

    {"cat": 6, "nr": 35, "titel": "Ertrinkungsgefahr",
     "text": "Bei Arbeiten an/über Gewässern: Massnahmen nach Art. 23 und 29. Falls technisch nicht möglich: Rettungswesten, Rettungsringe, Tauwerke. Bei fliessenden Gewässern mit Abschwemmgefahr: Auffangvorrichtungen oder motorisierte Rettungsboote."},

    {"cat": 6, "nr": 36, "titel": "Lärm",
     "text": "Kann die Lärmbelastung nicht unter den Grenzwert gesenkt werden, sind geeignete Gehörschutzmittel zu tragen."},

    {"cat": 6, "nr": 37, "titel": "Sonne, Hitze und Kälte",
     "text": "Bei Arbeiten bei Sonne, Hitze und Kälte sind die erforderlichen Massnahmen zum Schutz der Arbeitnehmer zu treffen."},

    {"cat": 6, "nr": 38, "titel": "Beleuchtung",
     "text": "Arbeitsplätze und Verkehrswege müssen über eine ausreichende Beleuchtung verfügen."},

    {"cat": 6, "nr": 39, "titel": "Naturgefahren",
     "text": "In Zonen mit Naturgefahren (Lawinen, Hochwasser, Murgänge, Erdrutsche, Steinschlag) darf nur gearbeitet werden, wenn: geeignete Überwachung gewährleistet, Rettungskräfte alarmiert werden können, Transport zum Arzt/Spital sichergestellt. Bei akuter Gefahr: keine Arbeitnehmer in der Gefahrenzone."},

    # ==========================================================
    # 2. KAPITEL / 7. ABSCHNITT: TRANSPORT (Art. 40)
    # ==========================================================
    {"cat": 7, "nr": 40, "titel": "Transport",
     "text": "Transportanlagen: direkte Sichtverbindung zwischen Steuerpersonal und jeder bedienten Stelle, sonst zuverlässiges Kommunikationssystem. Gefahrenbereich unterhalb Aufzugseinrichtungen absperren oder durch Warnposten sichern. Personentransporte nur mit dafür vorgesehenen Arbeitsmitteln."},

    # ==========================================================
    # 3. KAPITEL: ARBEITEN AUF DÄCHERN (Art. 41–46)
    # ==========================================================
    {"cat": 8, "nr": 41, "titel": "Massnahmen an Dachrändern",
     "text": "Ab Absturzhöhe über 2 m: geeignete Massnahmen an allen Dachrändern. Massgebend ist die Neigung an der Dachtraufe. Neigung <10°: Spenglergang oder durchgehender Seitenschutz. 10°–30°: Spenglergang. 30°–45°: Spenglergang mit Dachdeckerschutzwand. 45°–60°: Spenglergang mit Dachdeckerschutzwand plus zusätzliche Massnahmen (Arbeitspodeste/Seilsicherung). Giebelseitig: Geländerholm und Zwischenholm. Über 60°: nur von Gerüsten oder Hubarbeitsbühnen."},

    {"cat": 8, "nr": 42, "titel": "Dachfangwand bei Arbeiten auf bestehenden Dächern",
     "text": "Für Arbeiten auf bestehenden Dächern bis 45° Neigung kann eine Dachfangwand verwendet werden. Sie verhindert, dass Personen über den Dachrand abstürzen. Für dynamische Belastung bemessen. Direkt an der Traufe, mind. 80 cm Überstand, mind. 100 cm Bauhöhe, in tragender Unterkonstruktion verankert."},

    {"cat": 8, "nr": 43, "titel": "Schutz vor Abstürzen durch Öffnungen (Spenglergang–Fassade)",
     "text": "Beträgt die Öffnung zwischen Spenglergang-Belag und Fassade mehr als 30 cm, sind Massnahmen zu treffen, die Abstürze durch diese Öffnung verhindern."},

    {"cat": 8, "nr": 44, "titel": "Durchbruchsicherheit von Dachflächen",
     "text": "Vor Arbeitsbeginn: Abklärung, ob Dachflächen durchbruchsicher sind. Kann Durchbruchsicherheit nicht nachgewiesen werden, gelten sie als nicht durchbruchsicher. Bei Dachöffnungen: unabhängig von der Absturzhöhe tragfähige und unverrückbare Absturzsicherungen nach Art. 22–29."},

    {"cat": 8, "nr": 45, "titel": "Nicht durchbruchsichere Dachflächen",
     "text": "Arbeiten auf nicht durchbruchsicheren Dachflächen nur von Laufstegen aus. Sind Laufstege technisch nicht möglich: ab Absturzhöhe über 3 m Auffangnetze oder Fanggerüste. Nicht durchbruchsichere Flächen neben Arbeitsbereichen abschranken oder durchbruchsicher abdecken."},

    {"cat": 8, "nr": 46, "titel": "Arbeiten von geringem Umfang (auf Dächern)",
     "text": "Bei Arbeiten unter 2 Personenarbeitstagen pro Dach: Absturzsicherung erst ab Absturzhöhe über 3 m (bei Gleitgefahr ab 2 m). In jedem Fall: bis 60° Neigung: Seilsicherung; über 60°: Hubarbeitsbühne oder gleichwertig."},

    # ==========================================================
    # 4. KAPITEL: GERÜSTE – ALLGEMEINE BESTIMMUNGEN (Art. 47–52)
    # ==========================================================
    {"cat": 9, "nr": 47, "titel": "Trag- und Widerstandsfähigkeit",
     "text": "Nur Gerüste verwenden, die den Anforderungen des Produktesicherheitsgesetzes entsprechen. Gerüste müssen alle einwirkenden Kräfte aufnehmen können: Eigengewicht, Nutzlasten, Windkräfte, Schneelasten, dynamische Beanspruchung (Sprünge, Stürze, Erschütterungen) sowie spezielle Kräfte beim Auf-/Um-/Abbau."},

    {"cat": 9, "nr": 48, "titel": "Nicht zu benützende Gerüstbestandteile",
     "text": "Gerüstbestandteile, die verbogen, geknickt oder durch Korrosion oder anderswie beschädigt sind, dürfen nicht benützt werden."},

    {"cat": 9, "nr": 49, "titel": "Fundation",
     "text": "Gerüste müssen auf eine tragfähige Unterlage abgestellt und gegen Wegrutschen gesichert werden."},

    {"cat": 9, "nr": 50, "titel": "Stabilität",
     "text": "Gerüste sind so aufzubauen, dass sämtliche Bestandteile gegen unbeabsichtigtes Verschieben gesichert sind."},

    {"cat": 9, "nr": 51, "titel": "Verankerung",
     "text": "Das Gerüst ist am Bauwerk zug- und druckfest zu verankern oder anderweitig zu fixieren (Abstützen, Abspannen). Verankerung ist fortlaufend dem Gerüstaufbau/-abbau folgend zu montieren oder zu entfernen."},

    {"cat": 9, "nr": 52, "titel": "Ein- und Anbauten am Gerüst",
     "text": "Wer Aufzüge, Seilwinden, Konsolen, Werbetafeln, Verkleidungen etc. anbringen will, muss sich vergewissern, dass das Gerüst den Zusatzkräften standhält. Einwilligung des Gerüsterstellers erforderlich."},

    # ==========================================================
    # 4. KAPITEL: ARBEITSGERÜSTE (Art. 53–65)
    # ==========================================================
    {"cat": 10, "nr": 53, "titel": "Begriff (Arbeitsgerüste)",
     "text": "Arbeitsgerüste sind Konstruktionen, die begehbare Arbeitsflächen am Bauwerk schaffen. Sie können auch als Absturzsicherung dienen."},

    {"cat": 10, "nr": 54, "titel": "Verbot von Fassadengerüsten aus Holzstangen",
     "text": "Fassadengerüste dürfen nicht aus vertikal tragenden Holzstangen erstellt werden."},

    {"cat": 10, "nr": 55, "titel": "Tragfähigkeit und Belagsbreite",
     "text": "Leichtes Arbeitsgerüst (Verputz/Maler): 2,0 kN/m², mind. 60 cm Belagsbreite. Schweres Arbeitsgerüst (Maurer): 3,0 kN/m², mind. 90 cm. Besonders schweres Arbeitsgerüst (Fertigelemente): 4,5 kN/m², mind. 90 cm."},

    {"cat": 10, "nr": 56, "titel": "Zugänge zu Arbeitsplätzen (Gerüste)",
     "text": "Gerüstgänge müssen über Gerüsttreppen sicher zugänglich sein. Durchstiegsbeläge statt Treppen nur: a) am obersten Gang im Giebelbereich, b) bei Rollgerüsten, c) wenn Treppen aus Platzgründen nicht möglich. Max. 25 m Entfernung zu Treppe/Durchstieg. Ab 25 m Gerüsthöhe: mind. ein Aufzug für Material- und Personentransport. Stirnseitig: Seitenschutz nach Art. 22."},

    {"cat": 10, "nr": 57, "titel": "Gerüstgänge",
     "text": "Vertikaler Abstand der Gerüstgänge: mind. 1,9 m, max. 2,3 m. Ausnahme: unterste Durchgangshöhe vom Terrain und oberste über dem letzten Gang. Abstand Belag–Fassade: max. 30 cm in jeder Bauphase. Falls nicht einhaltbar: zusätzliche Absturzmassnahmen."},

    {"cat": 10, "nr": 58, "titel": "Spenglergang",
     "text": "Ermöglicht sicheres Arbeiten am Dachrand. Ab Absturzhöhe über 2 m: max. 1 m unterhalb Traufe/Flachdachrand. Belag für dynamische Beanspruchung (Sturz vom Dach) bemessen. Seitenschutz mind. 60 cm von Dachtraufe/Aussenkante entfernt. Oberster Holm mind. 80 cm über Dachrand."},

    {"cat": 10, "nr": 59, "titel": "Dachdeckerschutzwand",
     "text": "Schutzeinrichtung am Spenglergang, die vom Dach stürzende Personen, Gegenstände und Materialien auffängt. Öffnungen bis 100 cm² zulässig."},

    {"cat": 10, "nr": 60, "titel": "Montage und Demontage von Arbeitsgerüsten",
     "text": "Montage und Demontage hat gemäss den Herstellerangaben zu erfolgen."},

    {"cat": 10, "nr": 61, "titel": "Sichtkontrolle und Unterhalt",
     "text": "Der Arbeitgeber hat dafür zu sorgen, dass das Arbeitsgerüst täglich einer Sichtkontrolle unterzogen wird. Bei Mängeln: nicht benützen. Auf Gerüstbelägen und Zugängen: überflüssiges oder gefährliches Material (Schutt, Schnee, Eis) entfernen."},

    {"cat": 10, "nr": 62, "titel": "Nutzlast eines Arbeitsgerüstes / Materialpodestes",
     "text": "Die Nutzlast muss bei jedem Gerüstzugang gut sichtbar auf einem Schild angegeben sein. Gleiches gilt für Materialpodeste."},

    {"cat": 10, "nr": 63, "titel": "Sperrung des Arbeitsgerüstes",
     "text": "Gerüste oder Bereiche, die nicht zur Benutzung freigegeben sind, müssen mit einer technischen Massnahme (z.B. Seitenschutz) gesperrt werden."},

    {"cat": 10, "nr": 64, "titel": "Änderungen am Arbeitsgerüst",
     "text": "Änderungen dürfen nur vom Gerüstersteller vorgenommen werden. Geringfügige Anpassungen in Absprache mit dem Gerüstersteller (schriftlich)."},

    {"cat": 10, "nr": 65, "titel": "Besondere Bestimmungen für Rollgerüste",
     "text": "Vor Benützung: Standsicherheit prüfen (Art der Arbeiten, Bodenverhältnisse). Maximale Einsatzhöhe gemäss Verwendungsanleitung nicht überschreiten. Gegen unbeabsichtigtes Verschieben sichern. Während des Verschiebens: keine Personen auf dem Rollgerüst."},

    # ==========================================================
    # 4. KAPITEL: FANGGERÜSTE UND AUFFANGNETZE (Art. 66–67)
    # ==========================================================
    {"cat": 11, "nr": 66, "titel": "Fanggerüste",
     "text": "Fanggerüste fangen Personen, Gegenstände und Materialien auf. Max. Absturzhöhe: 2 m. Auskragende Montage: mind. 1,5 m horizontale Auskragung. Bei Absturzseite: Seitenschutz nach Art. 22. Belag für dynamische Beanspruchung bemessen."},

    {"cat": 11, "nr": 67, "titel": "Auffangnetze",
     "text": "Auffangnetze sind so anzubringen, dass Personen nicht tiefer als 3 m abstürzen können."},

    # ==========================================================
    # 5. KAPITEL: GRÄBEN, SCHÄCHTE UND BAUGRUBEN (Art. 68–80)
    # ==========================================================
    {"cat": 12, "nr": 68, "titel": "Allgemeines (Gräben/Schächte/Baugruben)",
     "text": "Gräben, Schächte und Baugruben sind so auszugestalten, dass niemand durch herabfallende oder abrutschende Massen gefährdet wird. Über 1,5 m Tiefe: abböschung nach Art. 75 oder andere geeignete Massnahmen, wenn nicht verspriesst."},

    {"cat": 12, "nr": 69, "titel": "Minimale lichte Breite in Gräben und Schächten",
     "text": "Lichte Breite muss sicheres Arbeiten gewährleisten. Für Werkleitungen ab 1 m Tiefe: mind. 60 cm. Innenrohrdurchmesser bis 40 cm: mind. 40 cm + Aussenrohrdurchmesser. Bis 120 cm: mind. 60 cm (eine Seite mind. 40 cm) + Aussenrohrdurchmesser. Ab 120 cm: mind. 80 cm (eine Seite mind. 60 cm) + Aussenrohrdurchmesser."},

    {"cat": 12, "nr": 70, "titel": "Minimale Breite des Arbeitsraums in Baugruben",
     "text": "Die Breite des Arbeitsraums in Baugruben muss in jeder Bauphase mindestens 60 cm betragen."},

    {"cat": 12, "nr": 71, "titel": "Freihaltung der Ränder von Gräben und Baugruben",
     "text": "Ränder horizontal freihalten: a) bei Spriessungen/Spund-/Schlitzwänden: mind. 50 cm. b) bei Böschungen: mind. 1 m."},

    {"cat": 12, "nr": 72, "titel": "Deponien von Aushub- und Baumaterial",
     "text": "Deponien sind so zu erstellen, dass keine Arbeitnehmer gefährdet werden."},

    {"cat": 12, "nr": 73, "titel": "Einsatz von Treppen und Leitern (Gräben)",
     "text": "Zugang zu Baugruben, Gräben und Schächten über sichere Arbeitsmittel (Treppen). Treppen alle 5 m mit Zwischenpodesten. Leitern statt Treppen: a) Baugruben bis 5 m wenn Treppen technisch nicht möglich, b) Gräben/Schächte bis 5 m."},

    {"cat": 12, "nr": 74, "titel": "Verhinderung des Überfahrens von Rändern",
     "text": "Gegen Überfahren von Graben-/Schacht-/Baugrubenrändern und Böschungskanten: Geschwindigkeitsbegrenzungen, Verkehrsführung mit Signalisation, Abschrankungen und Radabweiser."},

    {"cat": 12, "nr": 75, "titel": "Standfestigkeit des Baugrunds bei Böschungen",
     "text": "Böschungsneigungen der Standfestigkeit des Baugrunds anpassen. Bei Beeinträchtigung durch Niederschläge, Tauwetter, Lasten oder Erschütterungen: geeignete Massnahmen treffen."},

    {"cat": 12, "nr": 76, "titel": "Sicherheitsnachweis bei Böschungen",
     "text": "Sicherheitsnachweis eines Fachingenieurs/Geotechnikers nötig bei: a) Böschung über 4 m, b) Verhältnis Senkrechte:Waagrechte über 2:1 (gutes Material) bzw. 1:1 (rolliges Material), c) zusätzliche Belastung durch Fahrzeuge/Maschinen/Deponien, d) Hangwasser oder Grundwasser am Böschungsfuss."},

    {"cat": 12, "nr": 77, "titel": "Anforderungen an Spriessungen",
     "text": "Spriessungen müssen den Belastungen standhalten und nach Regeln der Technik ausgeführt werden. Zusätzliche Belastungen (Fahrzeuge, Maschinen, Deponien) bei Dimensionierung berücksichtigen."},

    {"cat": 12, "nr": 78, "titel": "Ausführung der Spriessungen",
     "text": "Benachbarte unverspriesste Wandteile dürfen niemanden gefährden. Unterster Teil der Grabenwand bis max. 80 cm unverspriesst (wenn Material zulässt). Zwischenräume bei standfestem Material: max. 20 cm. Hohlräume hinter Spriesswänden sofort satt auffüllen. Spriessungen müssen mind. 15 cm über Grabenrand vorstehen. Gräben unterhalb von Böschungen: gesamte vertikale Tiefe verspriessen. Beim Ein-/Ausbau: keine Personen im ungesicherten Bereich."},

    {"cat": 12, "nr": 79, "titel": "Sicherheitsnachweis bei Baugrundverbesserungen",
     "text": "Baugrundverbesserungen (Injektionen, Vermörtelungen, künstliche Vereisungen) nur mit Sicherheitsnachweis eines Fachingenieurs/Geotechnikers. Prüfungen und Messungen nach dessen Anweisungen."},

    {"cat": 12, "nr": 80, "titel": "Überhänge an Böschungen oder Grabenwänden",
     "text": "Überhänge sind unverzüglich zu beseitigen. Freigelegte Gegenstände (Bauwerksteile, Werkleitungen, Randsteine, Findlinge, Bäume) sind zu entfernen oder zu sichern."},

    # ==========================================================
    # 6. KAPITEL: RÜCKBAU- UND ABBRUCHARBEITEN (Art. 81–86)
    # ==========================================================
    {"cat": 13, "nr": 81, "titel": "Rückbau und Abbruch – Allgemeines",
     "text": "Im Sicherheitskonzept (Art. 4) festhalten: Massnahmen nach Art. 17, 22–29, 32–34. Zusätzlich verhindern, dass: Bauteile unbeabsichtigt einstürzen, Nachbarbauwerke instabil werden, beschädigte Werkleitungen oder Seilbruch gefährden. Gefahrenzonen durch Schutzwände/Absperrungen/Warnposten sichern. Nur unter ständiger fachkundiger Aufsicht."},

    {"cat": 13, "nr": 82, "titel": "Asbestsanierungsarbeiten – Grundsatz",
     "text": "Asbestsanierungen mit erheblicher Faserfreisetzung dürfen nur von Suva-anerkannten Asbestsanierungsunternehmen ausgeführt werden. Betrifft u.a.: Spritzbeläge, Boden-/Decken-/Wandbeläge, Fliesenkleber, Leichtbauplatten, Brandabschottungen, Dämmmaterialien, Schnüre/Matten, Mörtel/Putze, Karton mit Asbest."},

    {"cat": 13, "nr": 83, "titel": "Anerkennung von Asbestsanierungsunternehmen",
     "text": "Anerkennung wenn: a) eigener Spezialist für Asbestsanierungen beschäftigt und während Sanierung anwesend, b) mind. 2 weitere instruierte Arbeitnehmer, c) notwendige Arbeitsmittel und Instandhaltungsplan, d) Gewähr für Einhaltung des Rechts. Suva kann Anerkennung entziehen."},

    {"cat": 13, "nr": 84, "titel": "Anforderungen an Asbest-Spezialisten",
     "text": "Kenntnisse in: Arbeitssicherheit/Gesundheitsschutz, staubarme Entfernung, PSA-Verwendung, Arbeitsplanerstellung, Baustellentagebuch, Führen/Instruieren von Arbeitnehmern."},

    {"cat": 13, "nr": 85, "titel": "Fortbildung Asbest-Spezialisten",
     "text": "Mindestens alle 5 Jahre Fortbildung zur Vertiefung und Aktualisierung der Fachkenntnisse."},

    {"cat": 13, "nr": 86, "titel": "Meldepflicht für Asbestsanierungsunternehmen",
     "text": "Asbestsanierungen mind. 14 Tage vor Ausführung bei der Suva melden. Suva-Formulare verwenden."},

    # ==========================================================
    # 7. KAPITEL: UNTERTAGARBEITEN (Art. 87–101)
    # ==========================================================
    {"cat": 14, "nr": 87, "titel": "Meldepflicht (Untertagarbeiten)",
     "text": "Alle Untertagarbeiten mind. 14 Tage vor Ausführung der Suva melden. Ausgenommen: Kontrollarbeiten und kleinere Unterhaltsarbeiten an bestehenden Tunnels."},

    {"cat": 14, "nr": 88, "titel": "Sicherheitskonzept (Untertagarbeiten)",
     "text": "Im Sicherheitskonzept (Art. 4) sind die Massnahmen zur Umsetzung der Art. 89–101 festzuhalten."},

    {"cat": 14, "nr": 89, "titel": "Redundante Energieversorgung",
     "text": "Redundante Energieversorgung für: Schachtbefahranlagen, Erdgaswarnanlagen, Kommunikation, Druckluft bei Überdruck, Lüfter bei Erdgas, Beleuchtung, Pumpen bei gefluteten Fluchtwegen."},

    {"cat": 14, "nr": 90, "titel": "Klimatische Bedingungen (Untertag)",
     "text": "Bei Gefährdung durch besondere Wärme, Kälte, Luftfeuchtigkeit: geeignete Massnahmen treffen."},

    {"cat": 14, "nr": 91, "titel": "Belüftung (Untertag)",
     "text": "Vor Beginn: Lüftungskonzept erstellen. Arbeitsräume belüften. Zugang zu nicht belüfteten Räumen verboten. In Ausnahmen: ununterbrochene messtechnische Überwachung."},

    {"cat": 14, "nr": 92, "titel": "Erdgas in Gesteinsschichten",
     "text": "Abklärung, ob Erdgas vorhanden ist. Nötigenfalls geeignete Massnahmen."},

    {"cat": 14, "nr": 93, "titel": "Explosions- und Brandgefahr (Untertag)",
     "text": "Verbrennungsmotoren mit niedrigem Flammpunkt (Benzin, Flüssiggas) dürfen untertags nicht eingesetzt werden."},

    {"cat": 14, "nr": 94, "titel": "Beleuchtung (Untertag)",
     "text": "Nur mit installierter Notbeleuchtung oder wenn jede Person eine Lampe mitführt."},

    {"cat": 14, "nr": 95, "titel": "Arbeiten in Tunnels bei laufendem Verkehr",
     "text": "Geeignete Massnahmen, dass niemand durch vorbeifahrende Züge oder Fahrzeuge gefährdet wird."},

    {"cat": 14, "nr": 96, "titel": "Transport (Untertag)",
     "text": "Transportpisten, Gleis- und Bandanlagen sicher anlegen und unterhalten. Verkehrsmittel so ausrüsten, dass der Gefahrenbereich in Fahrtrichtung überblickt werden kann."},

    {"cat": 14, "nr": 97, "titel": "Schutz technischer Installationen und Gefahrstofflager",
     "text": "Technische Installationen (Lüftung, Frischluftzufuhr) und Gefahrstofflager, die bei Beschädigung Personen gefährden können, sind zu schützen."},

    {"cat": 14, "nr": 98, "titel": "Fusswege (Untertag)",
     "text": "Fusswege entlang Fahrpisten und Gleisanlagen sind mit technischen Massnahmen zu trennen. Ausnahme: Kontroll- und kleinere Unterhaltsarbeiten."},

    {"cat": 14, "nr": 99, "titel": "Schutz vor einbrechendem Gestein und Wassereinbruch",
     "text": "Vorerkundungen vor Ausbrucharbeiten. Arbeitsplätze sichern. Bei Bedarf: geeignete Hohlraumsicherung."},

    {"cat": 14, "nr": 100, "titel": "Sprengvortrieb",
     "text": "Schutz vor Druckstoss, Lärm, Steinwurf, Sprengschwaden. Arbeit an Sprengstelle frühestens 15 Minuten nach Sprengung. Nach jedem Abschlag: Materialablösungen und gelockerte Gesteinspartien entfernen."},

    {"cat": 14, "nr": 101, "titel": "Warnkleider (Untertag)",
     "text": "Warnkleider nach Art. 7, die den ganzen Körper bedecken."},

    # ==========================================================
    # 8. KAPITEL: ABBAU VON GESTEIN, KIES UND SAND (Art. 102–110)
    # ==========================================================
    {"cat": 15, "nr": 102, "titel": "Meldepflicht für den Abbau von Gestein",
     "text": "Abbau im Freien von über 5000 m³ pro Abbaustelle: mind. 14 Tage vor Ausführung der Suva melden."},

    {"cat": 15, "nr": 103, "titel": "Abbauplan",
     "text": "Vor Beginn Abbauplan erstellen. Muss Lagerungs-/Schichtverhältnisse, Standfestigkeit und maximale Böschungsneigungen berücksichtigen."},

    {"cat": 15, "nr": 104, "titel": "Böschungsneigung (Abraum)",
     "text": "Böschungsneigung von Abraumdecken max. 45°. Distanz Fusspunkt Abraum zu Böschungskante: mind. 1 m."},

    {"cat": 15, "nr": 105, "titel": "Abbau von Gestein durch Sprengung",
     "text": "Abbauwände in Stufen unterteilen. Max. Stufenhöhe: 40 m (Ausnahme: Naturwerkstein). Nach Sprengung: Stabilität durch Fachperson beurteilen. Materialablösungen und gelockerte Partien entfernen."},

    {"cat": 15, "nr": 106, "titel": "Abbau von Kies und Sand",
     "text": "Abbau von oben: in Stufen. Abbau von unten: nur in locker gelagertem Material. Wandhöhe: max. höchster erreichbarer Punkt + Raddurchmesser des Geräts. Bei Wasserstrahl: Wandhöhe nicht begrenzt wenn Standort ausserhalb Gefahrenbereich."},

    {"cat": 15, "nr": 107, "titel": "Verbot der Unterhöhlung von Abbauwänden",
     "text": "Abbauwände dürfen zu keinem Zeitpunkt unterhöhlt werden."},

    {"cat": 15, "nr": 108, "titel": "Absturzsicherung (Abbau)",
     "text": "Arbeitnehmer in steilem Gelände oder an Abbauwänden müssen nach Art. 22–29 gegen Absturz gesichert sein."},

    {"cat": 15, "nr": 109, "titel": "Schutz vor niedergehenden Steinen und Materialien",
     "text": "Schutz durch Massnahmen wie Schutzvorrichtungen an Fahrerkabinen. Drohende Materialabstürze: Bereich sofort absperren. Verkehrswege bei Steinschlaggefahr sichern."},

    {"cat": 15, "nr": 110, "titel": "Massnahmen vor Wiederaufnahme der Arbeiten",
     "text": "Nach Arbeitsunterbrüchen: überhängende Partien abbauen, loses Material aus Böschung entfernen."},

    # ==========================================================
    # 9. KAPITEL: WÄRMETECHNISCHE ANLAGEN UND HOCHKAMINE (Art. 111–117)
    # ==========================================================
    {"cat": 16, "nr": 111, "titel": "Begriffe (Wärmetechnische Anlagen/Hochkamine)",
     "text": "Wärmetechnische Anlagen: Feuerungsanlagen und stationäre Verbrennungsmotoren inkl. Wärmeerzeugungs-/-transport-/-verteileinrichtungen, Steuer- und Sicherheitseinrichtungen, Verbindungsrohre, Abgasanlagen. Hochkamine: freistehende, begehbare Abgasanlagen, die nur von oben nach unten gereinigt werden können."},

    {"cat": 16, "nr": 112, "titel": "Persönliche Anforderungen",
     "text": "Nur geeignete und instruierte Arbeitnehmer einsetzen. Mind. eine Person mit entsprechender Ausbildung muss ununterbrochen vor Ort sein."},

    {"cat": 16, "nr": 113, "titel": "Steuer- und Schalteinrichtungen",
     "text": "Jede Anlage muss von jeder Energiequelle abtrennbar sein. Bei Arbeiten an begehbaren Anlagen/Hochkaminen: Sicherheitsabschaltung mit Vorhängeschloss, Elektrostecker ziehen und Steckdose sichern, Hinweistafel anbringen."},

    {"cat": 16, "nr": 114, "titel": "Arbeiten an begehbaren Anlagen und Hochkaminen",
     "text": "Überwachung durch Person ausserhalb des Gefahrenbereichs. Erst betreten/besteigen wenn genügend abgekühlt und gesundheitsgefährdende Gase entfernt (Messung). Falls Gase nicht entfernbar: umgebungsunabhängige Atemschutzgeräte."},

    {"cat": 16, "nr": 115, "titel": "Zugänge zu Abgasanlagen auf Dächern",
     "text": "Nur begehen wenn feste Vorrichtungen vorhanden (Laufstege, feste Leitern). Sonst: Fanggerüste, Auffangnetze oder Seilsicherungen."},

    {"cat": 16, "nr": 116, "titel": "Besteigen von Hochkaminen",
     "text": "Von aussen: nur über ortsfeste Leitern oder für Personen zugelassene Transportmittel. Von innen: nur über bestehende Steigeisen in einwandfreiem Zustand."},

    {"cat": 16, "nr": 117, "titel": "Elektrische Anschlüsse über Dachständer",
     "text": "Im Arbeitsbereich: von Stromzuführung abtrennen oder gegen Berührung sichern. Leitungseigentümer vor Arbeitsaufnahme benachrichtigen."},

    # ==========================================================
    # 10. KAPITEL: ARBEITEN AM HÄNGENDEN SEIL (Art. 118)
    # ==========================================================
    {"cat": 17, "nr": 118, "titel": "Arbeiten am hängenden Seil",
     "text": "Nur Arbeitnehmer mit entsprechender Ausbildung. Fortbildung mind. alle 3 Jahre. Mind. 2 Arbeitnehmer zur gegenseitigen Überwachung. Seilsystem: mind. 2 getrennt befestigte Seile (Fortbewegung + Sicherung). Ausnahme für Einzelseil nur wenn Risikobewertung ergibt, dass zweites Seil gefährlicher wäre."},

    # ==========================================================
    # 11. KAPITEL: ARBEITEN IN ROHRLEITUNGEN (Art. 119)
    # ==========================================================
    {"cat": 18, "nr": 119, "titel": "Arbeiten in Rohrleitungen",
     "text": "Ununterbrochene Überwachung durch Person ausserhalb. Lichtmass 600–800 mm: mit Manipulatoren (von aussen bedient). Falls Manipulatoren nicht möglich: künstliche Belüftung, seilgeführte Rollenwagen ab 20 m, Flucht/Rettung und Kommunikation gewährleistet. Unter 600 mm Lichtmass: nur Manipulatoren."},
]
