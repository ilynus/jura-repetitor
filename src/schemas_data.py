"""Vorinstallierte Prüfungsschemata für das 1. Staatsexamen NRW.

Jedes Schema enthält:
- title: Bezeichnung
- topic: Rechtsgebiet (aus dem bekannten Topic-Enum)
- normen: Zentrale Normen
- examensrelevanz: 1–3 Sterne
- schema: Geordnete Liste von Prüfungspunkten (mit optionalen Unterpunkten)
- hinweise: Klausurtaktische Hinweise
- klassiker: Typische Examenskonstellationen

Die Bibliothek ist alphabetisch nach Rechtsgebiet, dann nach Häufigkeit sortiert.
Jederzeit durch KI-Generierung erweiterbar (siehe Schemata-Seite).
"""
from __future__ import annotations

SCHEMAS: list[dict] = [

    # ============================================================
    #  BGB AT
    # ============================================================
    {
        "id": "bgb_at_vertrag",
        "title": "Vertragsschluss (Angebot & Annahme)",
        "topic": "BGB AT",
        "normen": ["§§ 145–150 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Angebot",
            "   1. Willenserklärung",
            "   2. Inhaltliche Bestimmtheit (essentialia negotii)",
            "   3. Rechtsbindungswille",
            "   4. Zugang (§ 130 BGB)",
            "   5. Erlöschen: Frist, Tod/Geschäftsunfähigkeit, Widerruf (§ 130 Abs. 1 S. 2 BGB)",
            "II. Annahme",
            "   1. Willenserklärung",
            "   2. Rechtzeitigkeit (§§ 147 f. BGB)",
            "   3. Inhaltsidentität / Modifikation = neues Angebot (§ 150 Abs. 2 BGB)",
            "   4. Zugang",
            "III. Ergebnis: Vertrag (+/-)",
        ],
        "hinweise": "Beim invitatio ad offerendum (Schaufenster, Online-Shop) immer prüfen, wer Anbieter ist. § 151 BGB (Annahme ohne Erklärung) nicht vergessen.",
        "klassiker": ["Internetkauf: Wer macht das Angebot?", "verspätete Annahme § 150 Abs. 1 BGB", "automatische Auftragsbestätigung"],
    },
    {
        "id": "bgb_at_anfechtung",
        "title": "Anfechtung (§§ 119 ff., 123 BGB)",
        "topic": "BGB AT",
        "normen": ["§§ 119, 120, 121, 123, 142, 143 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Anfechtungsgrund",
            "   1. Inhaltsirrtum (§ 119 Abs. 1 Alt. 1 BGB)",
            "   2. Erklärungsirrtum (§ 119 Abs. 1 Alt. 2 BGB)",
            "   3. Eigenschaftsirrtum (§ 119 Abs. 2 BGB) — strenger Maßstab!",
            "   4. Übermittlungsirrtum (§ 120 BGB)",
            "   5. Arglistige Täuschung (§ 123 Abs. 1 Alt. 1 BGB)",
            "   6. Widerrechtliche Drohung (§ 123 Abs. 1 Alt. 2 BGB)",
            "II. Anfechtungserklärung (§ 143 BGB)",
            "   — gegenüber dem richtigen Anfechtungsgegner",
            "III. Anfechtungsfrist",
            "   — §§ 119, 120: unverzüglich (§ 121 BGB)",
            "   — § 123: 1 Jahr (§ 124 BGB)",
            "IV. Rechtsfolge: ex-tunc-Nichtigkeit (§ 142 Abs. 1 BGB)",
            "V. Schadensersatz (§ 122 BGB) — nur bei §§ 119, 120!",
        ],
        "hinweise": "Motivirrtum ist grundsätzlich unbeachtlich! Eigenschaftsirrtum (§ 119 II) ist Ausnahme. Kausalität bei § 123 prüfen. § 122 BGB nicht vergessen.",
        "klassiker": ["Zahlendreher beim Preis", "Eigenschaft einer Sache", "arglistige Täuschung durch Dritte (§ 123 Abs. 2 BGB)"],
    },
    {
        "id": "bgb_at_geschaeftsfaehigkeit",
        "title": "Geschäftsfähigkeit / §§ 104 ff. BGB",
        "topic": "BGB AT",
        "normen": ["§§ 104–113 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Geschäftsunfähigkeit (§ 104 BGB) → Nichtigkeit (§ 105 BGB)",
            "II. Beschränkte Geschäftsfähigkeit (§ 106 BGB, 7–18 Jahre)",
            "   1. Lediglich rechtlich vorteilhaft (§ 107 BGB)? → wirksam",
            "   2. Mit Einwilligung der Eltern (§ 107 BGB)? → wirksam",
            "   3. Taschengeldparagraph (§ 110 BGB)?",
            "      a) Mittel des täglichen Lebens",
            "      b) mit überlassenen Mitteln bewirkt",
            "   4. Genehmigung (§ 108 BGB): schwebend unwirksam bis Genehmigung/Verweigerung",
            "      — Zweiwochenfrist des § 108 Abs. 2 BGB beachten",
            "   5. Widerruf des anderen Teils (§ 109 BGB)",
            "III. Vollgeschäftsfähigkeit (§ 2 BGB, ab 18 Jahre)",
        ],
        "hinweise": "Lediglich rechtlich vorteilhaft: wirtschaftliche Betrachtung, nicht rechtliche Betrachtung. Schulden = nachteilig auch wenn wirtschaftlich sinnvoll.",
        "klassiker": ["15-Jähriger kauft Handy", "Schenkung an Minderjährigen mit Belastung", "§ 110 BGB Taschengeld"],
    },
    {
        "id": "bgb_at_stellvertretung",
        "title": "Stellvertretung (§§ 164 ff. BGB)",
        "topic": "BGB AT",
        "normen": ["§§ 164–181 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Zulässigkeit der Stellvertretung",
            "II. Eigene Willenserklärung des Vertreters",
            "III. Im Namen des Vertretenen (Offenkundigkeitsprinzip)",
            "   — Ausnahmen: Handelsgeschäfte (§ 344 HGB), Bargeschäfte",
            "IV. Mit Vertretungsmacht",
            "   1. Rechtsgeschäftlich: Vollmacht (§§ 166, 167 BGB)",
            "      a) Innenvollmacht / Außenvollmacht",
            "      b) Erlöschen (§ 168 BGB)",
            "      c) Anscheinsvollmacht / Duldungsvollmacht (nicht im Gesetz!)",
            "   2. Gesetzlich: §§ 1629, 1793 BGB",
            "   3. Organschaftlich: § 35 GmbHG, § 78 AktG",
            "V. Vertreter ohne Vertretungsmacht (§§ 177–180 BGB)",
            "   — Genehmigung / Haftung § 179 BGB",
            "VI. Insichgeschäft (§ 181 BGB)",
        ],
        "hinweise": "Offenkundigkeitsprinzip und seine Ausnahmen. Duldungs- und Anscheinsvollmacht sind Gewohnheitsrecht, nicht im BGB. § 179 BGB: Wahl zwischen Erfüllung und Schadensersatz.",
        "klassiker": ["Anscheinsvollmacht (Kassierer)", "Insichgeschäft", "Erlöschen der Vollmacht und Gutglaubensschutz §§ 170–173 BGB"],
    },

    # ============================================================
    #  SCHULDRECHT AT
    # ============================================================
    {
        "id": "schuldR_at_280",
        "title": "Schadensersatz wegen Pflichtverletzung (§ 280 Abs. 1 BGB)",
        "topic": "SchuldR AT",
        "normen": ["§§ 280, 241 Abs. 2, 276, 249 ff. BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Schuldverhältnis",
            "II. Pflichtverletzung (§ 241 Abs. 2 BGB)",
            "   — Leistungs- oder Schutzpflichtverletzung",
            "III. Vertretenmüssen (§ 280 Abs. 1 S. 2 BGB) — Vermutung!",
            "   1. Vorsatz oder Fahrlässigkeit (§ 276 BGB)",
            "   2. Zurechnung von Erfüllungsgehilfen (§ 278 BGB)",
            "IV. Schaden",
            "   1. Haftungsbegründende Kausalität",
            "   2. Haftungsausfüllende Kausalität",
            "   3. Zurechnung (Adäquanz, Schutzzweck der Norm)",
            "V. Kein Ausschluss (§§ 307 ff. BGB, Mitverschulden § 254 BGB)",
            "VI. Rechtsfolge: §§ 249 ff. BGB (Natural-/Geldersatz)",
        ],
        "hinweise": "§ 280 I ist die Grundnorm. Für Verzug: §§ 280 I, II, 286. Für Nichtleistung: §§ 280 I, III, 283/281. Fristsetzung bei § 281 nicht vergessen.",
        "klassiker": ["Schlechtleistung beim Werkvertrag", "pVV / Schutzpflichtverletzung", "Verzug §§ 286, 288 BGB"],
    },
    {
        "id": "schuldR_at_ruecktritt",
        "title": "Rücktritt (§§ 323, 326 BGB)",
        "topic": "SchuldR AT",
        "normen": ["§§ 323–326, 346 ff. BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Rücktrittsrecht",
            "   1. § 323 BGB: Nicht-/Schlechtleistung nach erfolgloser Fristsetzung",
            "      a) Fälliger, durchsetzbarer Anspruch",
            "      b) Nicht- oder Schlechtleistung",
            "      c) Fristsetzung (oder Entbehrlichkeit § 323 Abs. 2 BGB)",
            "   2. § 324 BGB: Verletzung Schutzpflicht",
            "   3. § 326 Abs. 5 BGB: Unmöglichkeit",
            "   4. Vertraglich vereinbartes Rücktrittsrecht",
            "II. Ausschluss (§ 323 Abs. 5, 6 BGB)",
            "   — Unerhebliche Pflichtverletzung (Abs. 5 S. 2)",
            "   — Alleinverantwortlichkeit des Gläubigers (Abs. 6)",
            "III. Rücktrittserklärung (§ 349 BGB)",
            "IV. Rechtsfolge: Rückgewährschuldverhältnis (§§ 346 ff. BGB)",
            "   1. Herausgabe der empfangenen Leistungen",
            "   2. Wertersatz bei Unmöglichkeit der Herausgabe (§ 346 Abs. 2 BGB)",
            "   3. Nutzungsherausgabe",
        ],
        "hinweise": "Unerheblichkeit (§ 323 V 2) ist eine Einrede, muss geprüft werden! Verhältnis Rücktritt/Schadensersatz: §§ 325, 280 I, III, 281 BGB.",
        "klassiker": ["mangelhafte Kaufsache, keine Nacherfüllung", "Frist entbehrlich bei ernsthafter Verweigerung", "Rücktritt + Schadensersatz kombiniert"],
    },

    # ============================================================
    #  SCHULDRECHT BT
    # ============================================================
    {
        "id": "schuldR_bt_kaufvertrag",
        "title": "Sachmangel / Nacherfüllung (§§ 434, 437 BGB)",
        "topic": "SchuldR BT",
        "normen": ["§§ 433, 434, 437–441 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Kaufvertrag (§ 433 BGB)",
            "II. Sachmangel bei Gefahrübergang (§ 434 BGB)",
            "   1. Subjektiver Fehlerbegriff (§ 434 Abs. 2 BGB)",
            "      a) Vereinbarte Beschaffenheit",
            "      b) Eignung für vertraglich vorausgesetzten Verwendungszweck",
            "   2. Objektiver Fehlerbegriff (§ 434 Abs. 3 BGB)",
            "      — Eignung für gewöhnlichen Verwendungszweck",
            "      — Beschaffenheit üblicher Sachen gleicher Art",
            "   3. Montagemangel (§ 434 Abs. 4 BGB)",
            "   4. Rechtsmangel (§ 435 BGB)",
            "III. Gefahrübergang (§§ 446, 447 BGB)",
            "IV. Rechte des Käufers (§ 437 BGB)",
            "   1. Nacherfüllung (§§ 437 Nr. 1, 439 BGB) — Vorrang!",
            "      — Fristsetzung erforderlich für weitere Rechte",
            "   2. Rücktritt (§§ 437 Nr. 2, 323, 326 BGB)",
            "   3. Minderung (§§ 437 Nr. 2, 441 BGB)",
            "   4. Schadensersatz (§§ 437 Nr. 3, 280 ff. BGB)",
            "   5. Aufwendungsersatz (§§ 437 Nr. 3, 284 BGB)",
            "V. Verjährung (§ 438 BGB): 2 Jahre ab Übergabe",
        ],
        "hinweise": "IMMER: Nacherfüllung geht vor! Fristsetzung für Rücktritt/SE erforderlich. § 442 BGB (Kenntnis des Käufers) prüfen. § 476 BGB Beweislastumkehr (Verbrauchsgüterkauf).",
        "klassiker": ["Gebrauchtwagenkauf (Unfallwagen)", "Unternehmer verkauft an Verbraucher § 476 BGB", "Nacherfüllungsort § 439 Abs. 2 BGB"],
    },

    # ============================================================
    #  SACHENRECHT
    # ============================================================
    {
        "id": "sachenR_eigentum_929",
        "title": "Eigentumsübertragung bewegliche Sachen (§§ 929 ff. BGB)",
        "topic": "SachenR",
        "normen": ["§§ 929–936 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Einigung (§ 929 S. 1 BGB) — dinglicher Vertrag",
            "   — Bestimmtheitsgrundsatz",
            "   — Bedingungsfeindlichkeit (§ 925 Abs. 2 BGB analog)",
            "II. Übergabe (§ 929 S. 1 BGB)",
            "   — Besitzverschaffung, Besitzaufgabe des Veräußerers",
            "   Alternativ: §§ 929 S. 2, 930, 931 BGB (Übergabesurrogate)",
            "III. Berechtigung des Veräußerers",
            "   1. Eigentümer (Regelfall)",
            "   2. Ermächtigung des Eigentümers",
            "   3. Gutgläubiger Erwerb (§§ 932 ff. BGB)",
            "      a) Rechtsgeschäftlicher Erwerb",
            "      b) Kein Abhandenkommen (§ 935 BGB)",
            "      c) Guter Glaube an Eigentümerstellung",
            "         — § 932 Abs. 2 BGB: Grob fahrlässige Unkenntnis schadet",
        ],
        "hinweise": "Abstraktionsprinzip: Schuldvertrag (z.B. Kauf) und dinglicher Vollzug sind zu trennen. Anwartschaftsrecht beim verlängerten Eigentumsvorbehalt nicht vergessen.",
        "klassiker": ["Eigentumsvorbehalt §§ 158, 929 BGB", "gutgläubiger Erwerb vom Nichtberechtigten", "Sicherungsübereignung § 930 BGB"],
    },
    {
        "id": "sachenR_985",
        "title": "Herausgabeanspruch (§ 985 BGB)",
        "topic": "SachenR",
        "normen": ["§§ 985–1007 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Eigentümerstellung des Klägers",
            "   — ggf. Durchgangserwerb, Surrogation prüfen",
            "II. Besitz des Beklagten",
            "   — auch mittelbarer Besitz ausreichend",
            "III. Kein Recht zum Besitz (§ 986 BGB)",
            "   1. Eigenes Besitzrecht",
            "   2. Abgeleitetes Besitzrecht (vom Eigentümer oder Berechtigten)",
            "IV. Ergebnis: Herausgabepflicht",
            "V. Ggf. Anspruchskonkurrenz",
            "   — §§ 987 ff. BGB (EBV) für Nutzungen/Schäden",
            "   — § 812 BGB nur, wenn kein EBV",
        ],
        "hinweise": "EBV-System (§§ 987–1003 BGB) hat Vorrang vor § 812 BGB! Gut/bösgläubig entscheidet über Haftungsumfang. §§ 994 ff. BGB für Verwendungen.",
        "klassiker": ["gestohlene Sache", "EBV vs. § 812 BGB Konkurrenz", "Verwendungsersatz §§ 994 ff. BGB"],
    },

    # ============================================================
    #  DELIKTSRECHT
    # ============================================================
    {
        "id": "deliktsR_823_1",
        "title": "§ 823 Abs. 1 BGB — Deliktische Haftung",
        "topic": "SchuldR BT",
        "normen": ["§§ 823 Abs. 1, 249 ff., 254 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Rechtsgutsverletzung",
            "   — Leben, Körper, Gesundheit, Freiheit, Eigentum",
            "   — sonstiges Recht (Besitz h.M., APR, Recht am Unternehmen)",
            "II. Verletzungshandlung",
            "III. Haftungsbegründende Kausalität (Äquivalenz + Adäquanz)",
            "IV. Rechtswidrigkeit",
            "   — indiziert durch Rechtsgutverletzung",
            "   — Rechtfertigungsgründe: §§ 227, 228, 904 BGB; Einwilligung",
            "V. Verschulden (§ 276 BGB)",
            "   1. Deliktsfähigkeit (§§ 827, 828 BGB)",
            "   2. Vorsatz oder Fahrlässigkeit",
            "   3. Zurechnung § 831 BGB (Verrichtungsgehilfe)",
            "VI. Schaden",
            "VII. Haftungsausfüllende Kausalität",
            "VIII. Umfang: §§ 249 ff. BGB; Mitverschulden § 254 BGB",
        ],
        "hinweise": "Reine Vermögensschäden sind NICHT über § 823 I ersatzfähig (kein sonstiges Recht!). § 826 BGB oder § 823 II BGB i.V.m. Schutzgesetz prüfen.",
        "klassiker": ["Verletzung des APR", "Recht am Gewerbebetrieb", "§ 831 BGB Entlastungsbeweis"],
    },

    # ============================================================
    #  BEREICHERUNGSRECHT
    # ============================================================
    {
        "id": "bereicherungsR_812",
        "title": "Ungerechtfertigte Bereicherung (§ 812 BGB)",
        "topic": "SchuldR BT",
        "normen": ["§§ 812–822 BGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Etwas erlangt",
            "   — Jeder vermögenswerte Vorteil (Besitz, Eigentum, Forderung, ...)",
            "II. Durch Leistung ODER in sonstiger Weise",
            "   A. Leistungskondiktion (§ 812 Abs. 1 S. 1 Alt. 1 BGB)",
            "      — bewusste, zweckgerichtete Mehrung fremden Vermögens",
            "      — Leistungsbeziehung bestimmt Kondiktionspartner!",
            "   B. Nichtleistungskondiktion (§ 812 Abs. 1 S. 1 Alt. 2 BGB)",
            "      — Eingriffs-, Rückgriffs-, Verwendungskondiktion",
            "III. Ohne rechtlichen Grund",
            "   — Wirksamer Behaltensgrund fehlt oder entfällt",
            "   — § 812 Abs. 1 S. 2 BGB: condictio ob causam finitam",
            "IV. Rechtsfolge: Herausgabe des Erlangten (§§ 818 ff. BGB)",
            "   — Gutgläubigkeit: § 818 Abs. 3 BGB (Wegfall der Bereicherung)",
            "   — Bösgläubigkeit: § 819 BGB (verschärfte Haftung)",
        ],
        "hinweise": "Subsidiarität: EBV (§§ 987 ff.) hat Vorrang. Leistungskondiktion geht Nichtleistungskondiktion vor im Mehrpersonenverhältnis (Durchgriffsverbot).",
        "klassiker": ["Anweisungsfall / Zession", "Leistung auf fehlerhafte Anweisung", "§ 817 S. 2 BGB Kondiktionssperre"],
    },

    # ============================================================
    #  STRAFRECHT AT
    # ============================================================
    {
        "id": "strafR_at_aufbau_begehung",
        "title": "Vorsätzliches Begehungsdelikt (Grundaufbau)",
        "topic": "StrafR AT",
        "normen": ["§§ 15, 16, 17 StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Tatbestand",
            "   1. Objektiver Tatbestand",
            "      a) Tatsubjekt (Sonderdelikte?)",
            "      b) Tathandlung",
            "      c) Taterfolg (bei Erfolgsdelikten)",
            "      d) Kausalität (Äquivalenztheorie)",
            "      e) Objektive Zurechnung",
            "         — Schaffung/Realisierung einer rechtlich missbilligten Gefahr",
            "   2. Subjektiver Tatbestand",
            "      a) Vorsatz (§ 15 StGB): Wissen und Wollen",
            "         — dolus directus 1°/2°, dolus eventualis",
            "      b) Besondere subjektive Merkmale (Absichten etc.)",
            "II. Rechtswidrigkeit",
            "   — indiziert durch TB-Verwirklichung",
            "   — Rechtfertigungsgründe: §§ 32, 34 StGB; §§ 227, 904 BGB analog",
            "III. Schuld",
            "   1. Schuldfähigkeit (§§ 19, 20, 21 StGB)",
            "   2. Unrechtsbewusstsein / Verbotsirrtum (§ 17 StGB)",
            "   3. Entschuldigungsgründe: §§ 33, 35 StGB",
            "   4. Zumutbarkeit normgemäßen Verhaltens",
            "IV. Strafzumessung / Versuch (§§ 22–24 StGB) ggf. vorher",
        ],
        "hinweise": "Objektive Zurechnung nicht vergessen! Irrtümer: § 16 StGB (TB-Irrtum) vs. § 17 StGB (Verbotsirrtum). Intensive Ausführung nur bei echten Problemen.",
        "klassiker": ["aberratio ictus", "error in persona", "dolus eventualis vs. bewusste Fahrlässigkeit"],
    },
    {
        "id": "strafR_at_notwehr",
        "title": "Notwehr (§ 32 StGB)",
        "topic": "StrafR AT",
        "normen": ["§ 32 StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Notwehrlage",
            "   1. Angriff: menschliches Verhalten",
            "   2. Auf Rechtsgüter des Täters oder Dritter",
            "   3. Gegenwärtig: unmittelbar bevorstehend / noch andauernd",
            "   4. Rechtswidrig: objektiv rechtswidrig",
            "II. Notwehrhandlung",
            "   1. Verteidigung (gegen den Angreifer gerichtet!)",
            "   2. Erforderlichkeit: geeignetstes, mildestes Mittel",
            "   3. Gebotenheit: sozialethische Einschränkungen",
            "      — Provokation, krasses Missverhältnis, nahe Angehörige",
            "      — Angriff von Schuldlosen (Kinder, Geisteskranke)",
            "III. Subjektives Rechtfertigungselement: Verteidigungswille",
            "IV. Notwehrexzess (§ 33 StGB): Entschuldigung bei asthenischen Affekten",
        ],
        "hinweise": "Gebotenheit (sozialethische Einschränkungen) sind das schwierige Klausurthema. § 33 StGB gilt nur bei asthenischen Affekten (Angst, Verwirrung), nicht bei sthenischen (Wut, Zorn).",
        "klassiker": ["Provokation der Notwehrlage", "Schutzwehr bei körperlich unterlegenem Angreifer", "§ 33 StGB bei Erschrecken"],
    },
    {
        "id": "strafR_at_versuch",
        "title": "Versuch (§§ 22–24 StGB)",
        "topic": "StrafR AT",
        "normen": ["§§ 22, 23, 24 StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Vorprüfung: Nichtvollendung + Strafbarkeit des Versuchs (§ 23 StGB)",
            "II. Tatentschluss (subjektiver TB + dolus directus 2° mind.)",
            "   — Vollendungsvorsatz erforderlich",
            "III. Unmittelbares Ansetzen (§ 22 StGB)",
            "   — Rspr./h.L.: Schwelle zum 'Jetzt geht's los'",
            "   — kritischer Punkt: Mittäterschaft (§ 25 Abs. 2 StGB)",
            "IV. Rechtswidrigkeit + Schuld",
            "V. Kein Rücktritt (§ 24 StGB)",
            "   1. Unbeendeter Versuch: freiwilliges Aufgeben",
            "   2. Beendeter Versuch: freiwilliges Verhindern der Vollendung",
            "   3. Fehlgeschlagener Versuch: kein Rücktritt möglich",
            "   4. Rücktritt bei Mittäterschaft: § 24 Abs. 2 StGB",
        ],
        "hinweise": "Abgrenzung unbeendet/beendet nach dem Vorstellungsbild des Täters bei der letzten Ausführungshandlung. Freiwilligkeit: ursächliche Eigenentscheidung.",
        "klassiker": ["Abgrenzung Vorbereitung / Versuch", "fehlgeschlagener Versuch", "Rücktritt bei Mittätern"],
    },
    {
        "id": "strafR_at_taeterschaft",
        "title": "Täterschaft und Teilnahme (§§ 25–27 StGB)",
        "topic": "StrafR AT",
        "normen": ["§§ 25–27, 29 StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Täterschaft (§ 25 StGB)",
            "   1. Unmittelbare Täterschaft (§ 25 Abs. 1 Alt. 1 StGB)",
            "   2. Mittelbare Täterschaft (§ 25 Abs. 1 Alt. 2 StGB)",
            "      — Werkzeug ohne Vorsatz / ohne Schuld / mit Irrtum",
            "   3. Mittäterschaft (§ 25 Abs. 2 StGB)",
            "      a) Gemeinsamer Tatentschluss",
            "      b) Gemeinsame Tatausführung (Tatherrschaft)",
            "      — Zurechnung der Beiträge; Exzess des Mittäters",
            "II. Anstiftung (§ 26 StGB)",
            "   1. Vorsätzliche rechtswidrige Haupttat (Akzessorietät)",
            "   2. Bestimmen: Hervorrufen des Tatentschlusses",
            "   3. Doppelter Anstiftervorsatz",
            "III. Beihilfe (§ 27 StGB)",
            "   1. Vorsätzliche rechtswidrige Haupttat",
            "   2. Hilfeleisten (physisch/psychisch)",
            "   3. Doppelter Gehilfenvorsatz",
            "   4. Strafmilderung (§ 27 Abs. 2, § 49 Abs. 1 StGB)",
            "IV. Limitierte Akzessorietät (§ 29 StGB)",
        ],
        "hinweise": "Tatherrschaftslehre vs. subjektive Theorie (BGH). Bei Mittäterschaft: Hintermann kann Mittäter sein. Sukzessive Mittäterschaft und Beihilfe abgrenzen.",
        "klassiker": ["Bandenchef als mittelbarer Täter / Mittäter", "Kettenanstiftung", "psychische Beihilfe durch Bestärken"],
    },

    # ============================================================
    #  STRAFRECHT BT
    # ============================================================
    {
        "id": "strafR_bt_diebstahl",
        "title": "Diebstahl (§ 242 StGB)",
        "topic": "StrafR BT",
        "normen": ["§§ 242–244a StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Objektiver Tatbestand",
            "   1. Fremde bewegliche Sache",
            "   2. Wegnahme: Bruch fremden + Begründung eigenen Gewahrsams",
            "      — Gewahrsamsbegriff: tatsächliche Herrschaft + Herrschaftswille",
            "      — Gewahrsamsenklave, Gewahrsamslockerung",
            "II. Subjektiver Tatbestand",
            "   1. Vorsatz",
            "   2. Zueignungsabsicht",
            "      a) Enteignungskomponente (dauerhaft)",
            "      b) Aneignungskomponente (zumindest vorübergehend)",
            "      c) Rechtswidrigkeit der beabsichtigten Zueignung",
            "III. Rechtswidrigkeit + Schuld",
            "IV. Qualifikationen",
            "   — § 243 StGB (besonders schwerer Fall)",
            "   — § 244 StGB (Bandendiebstahl, Waffe)",
        ],
        "hinweise": "Abgrenzung Diebstahl/Betrug/Unterschlagung: Wegnahme vs. Täuschung vs. schon in eigenem Gewahrsam. § 248a BGB beachten (Geringwertigkeit).",
        "klassiker": ["Tanken ohne zu zahlen", "Diebstahl mit Einbruch § 243", "Unterschlagung vs. Diebstahl"],
    },
    {
        "id": "strafR_bt_betrug",
        "title": "Betrug (§ 263 StGB)",
        "topic": "StrafR BT",
        "normen": ["§§ 263–265b StGB"],
        "examensrelevanz": 3,
        "schema": [
            "I. Objektiver Tatbestand (Kausalitätskette!)",
            "   1. Täuschung über Tatsachen",
            "      — ausdrücklich, konkludent, durch Unterlassen (§ 13 StGB)",
            "   2. Irrtum des Opfers (Kausalität: Täuschung → Irrtum)",
            "   3. Vermögensverfügung (durch das Opfer selbst!)",
            "   4. Vermögensschaden",
            "      — Vermögensvergleich vor/nach Verfügung",
            "      — Gesamtsaldierung",
            "II. Subjektiver Tatbestand",
            "   1. Vorsatz",
            "   2. Bereicherungsabsicht (eigene oder Dritter)",
            "   3. Rechtswidrigkeit der erstrebten Bereicherung",
            "   4. Stoffgleichheit",
            "III. Qualifikationen",
            "   — § 263 Abs. 3 StGB (besonders schwerer Fall)",
            "   — § 263 Abs. 5 StGB (gewerbsmäßig/Bande)",
        ],
        "hinweise": "Stoffgleichheit: Bereicherung muss Kehrseite des Schadens sein. Computerbetrug § 263a prüfen, wenn kein menschlicher Irrtum. Dreiecksbetrug: Näheverhältnis.",
        "klassiker": ["Dreiecksbetrug vs. Diebstahl in mittelbarer Täterschaft", "konkludente Täuschung beim Scheckeinsatz", "§ 263a Computerbetrug"],
    },

    # ============================================================
    #  ÖFFENTLICHES RECHT
    # ============================================================
    {
        "id": "oeffentlichR_grundrechte",
        "title": "Grundrechtsprüfung (allgemeines Schema)",
        "topic": "GR",
        "normen": ["Art. 1–19 GG"],
        "examensrelevanz": 3,
        "schema": [
            "I. Schutzbereich",
            "   1. Sachlicher Schutzbereich",
            "   2. Persönlicher Schutzbereich (Jedermannsrechte vs. Deutschenrechte)",
            "II. Eingriff",
            "   1. Klassischer Eingriff: final, unmittelbar, rechtsförmig, imperativ",
            "   2. Moderner Eingriffsbegriff (mittelbar-faktisch, wenn zurechenbar)",
            "III. Verfassungsrechtliche Rechtfertigung",
            "   1. Schranken",
            "      a) Gesetzesvorbehalt (einfacher / qualifizierter)",
            "      b) Verfassungsimmanente Schranken (kollidierendes Verfassungsrecht)",
            "   2. Schranken-Schranken",
            "      a) Formelle Rechtmäßigkeit des Gesetzes",
            "      b) Materielle Rechtmäßigkeit",
            "         — Bestimmtheitsgrundsatz",
            "         — Verhältnismäßigkeit: Legitimer Zweck, Geeignetheit, Erforderlichkeit, Angemessenheit",
            "         — Wesensgehalt (Art. 19 Abs. 2 GG)",
            "IV. Ergebnis",
        ],
        "hinweise": "Verhältnismäßigkeit ist fast immer das Schwerpunktproblem. Niemals 'Verhältnismäßigkeit' ohne Prüfung aller 4 Stufen. Art. 19 III GG bei juristischen Personen!",
        "klassiker": ["Berufsfreiheit Art. 12 GG (Dreistufentheorie)", "Art. 14 GG Eigentum/Enteignung", "Meinungsfreiheit Art. 5 GG vs. Ehrenschutz"],
    },
    {
        "id": "oeffentlichR_anfechtungsklage",
        "title": "Anfechtungsklage (§ 42 Abs. 1 Alt. 1 VwGO)",
        "topic": "VerwProzR",
        "normen": ["§§ 40–42, 68–73, 113 VwGO"],
        "examensrelevanz": 3,
        "schema": [
            "A. Zulässigkeit",
            "   I. Verwaltungsrechtsweg (§ 40 VwGO)",
            "   II. Statthafte Klageart: VA i.S.d. § 35 VwVfG NRW",
            "   III. Klagebefugnis (§ 42 Abs. 2 VwGO)",
            "      — Möglichkeit der Verletzung eigener subjektiver Rechte",
            "      — Adressatentheorie / Drittschutz",
            "   IV. Vorverfahren (§§ 68 ff. VwGO)",
            "      — Widerspruchsbehörde, Form, Frist (1 Monat)",
            "      — Entbehrlichkeit (§ 68 Abs. 1 S. 2 VwGO i.V.m. Landesrecht)",
            "   V. Klagefrist (§ 74 VwGO): 1 Monat nach Zustellung Widerspruchsbescheid",
            "   VI. Klagegegner (§ 78 VwGO): Behörde / Rechtsträger",
            "   VII. Beteiligten- und Prozessfähigkeit",
            "   VIII. Rechtsschutzbedürfnis",
            "B. Begründetheit (§ 113 Abs. 1 S. 1 VwGO)",
            "   — VA rechtswidrig + Kläger in subjektiven Rechten verletzt",
            "   I. Formelle Rechtmäßigkeit des VA",
            "      1. Zuständigkeit (sachlich, örtlich, instanziell)",
            "      2. Verfahren (§§ 9 ff. VwVfG NRW; Anhörung § 28 VwVfG NRW)",
            "      3. Form (§ 37 VwVfG NRW; Begründung § 39 VwVfG NRW)",
            "   II. Materielle Rechtmäßigkeit",
            "      1. Ermächtigungsgrundlage",
            "      2. Tatbestandsvoraussetzungen",
            "      3. Rechtsfolge (geb. Entscheidung / Ermessen § 40 VwVfG NRW)",
            "      4. Verhältnismäßigkeit",
        ],
        "hinweise": "NRW: §§ 68 ff. VwGO → AGVwGO NRW prüfen (Entbehrlichkeit Widerspruch!). Klagegegner nach § 78 VwGO: in NRW Behördenprinzip. Begründetheit: immer formell VOR materiell!",
        "klassiker": ["Baugenehmigung (Drittschutz Nachbar)", "Gewerbeuntersagung § 35 GewO", "Auflage/Nebenbestimmung anfechten"],
    },
    {
        "id": "oeffentlichR_polizeirecht_nrw",
        "title": "Ordnungsverfügung / Polizeirecht NRW",
        "topic": "PolR NRW",
        "normen": ["§§ 14, 15 OBG NRW", "§§ 8, 24 PolG NRW"],
        "examensrelevanz": 3,
        "schema": [
            "I. Ermächtigungsgrundlage",
            "   — § 14 OBG NRW (Ordnungsbehörden) oder",
            "   — § 8 PolG NRW (Polizei, Gefahr für die öffentliche Sicherheit)",
            "   — Spezialvorschriften vorgehen lassen!",
            "II. Formelle Rechtmäßigkeit",
            "   1. Zuständigkeit: OBG oder PolG NRW; örtl. Zuständigkeit",
            "   2. Verfahren: Anhörung § 28 VwVfG NRW",
            "   3. Form: Begründung § 39 VwVfG NRW",
            "III. Materielle Rechtmäßigkeit",
            "   1. Gefahr für die öffentliche Sicherheit oder Ordnung",
            "      a) Öffentliche Sicherheit: Normen, subjektive Rechte, Staat",
            "      b) Konkrete Gefahr: Wahrscheinlichkeit × Schadensgewicht",
            "   2. Verantwortlichkeit (Störer)",
            "      a) Verhaltensstörer (§ 17 OBG / § 4 PolG NRW)",
            "      b) Zustandsstörer (§ 18 OBG / § 5 PolG NRW)",
            "      c) Nichtstörer (§ 19 OBG / § 6 PolG NRW) — subsidiär!",
            "   3. Ermessen (Entschließungs- und Auswahlermessen)",
            "   4. Verhältnismäßigkeit: §§ 15–17 OBG NRW / §§ 2, 15 PolG NRW",
        ],
        "hinweise": "NRW: OBG für Ordnungsbehörden, PolG für Polizei. Doppelzuständigkeit beachten. Verhaltensstörer: unmittelbarer Verursacher. Anscheinsgefahr: objektiv und subjektiv.",
        "klassiker": ["Abschleppen (Zustandsstörer: Eigentümer vs. Fahrer)", "Scheinverursacher (Putativstörer)", "Gefahr im Verzug → Polizei statt Ordnungsbehörde"],
    },
    {
        "id": "oeffentlichR_verfassungsbeschwerde",
        "title": "Verfassungsbeschwerde (§§ 90 ff. BVerfGG)",
        "topic": "GR",
        "normen": ["Art. 93 Abs. 1 Nr. 4a GG", "§§ 90–95 BVerfGG"],
        "examensrelevanz": 3,
        "schema": [
            "A. Zulässigkeit",
            "   I. Zuständigkeit des BVerfG (Art. 93 Abs. 1 Nr. 4a GG)",
            "   II. Beschwerdefähigkeit (§ 90 Abs. 1 BVerfGG)",
            "      — Jedermann: nat. + jur. Personen des Privatrechts",
            "      — Art. 19 Abs. 3 GG bei jur. Personen",
            "   III. Beschwerdegegenstand (§ 90 Abs. 1 BVerfGG)",
            "      — Akte der öffentlichen Gewalt: Exekutive, Legislative, Judikative",
            "   IV. Beschwerdebefugnis",
            "      — Selbst, gegenwärtig, unmittelbar betroffen",
            "      — Möglichkeit der Grundrechtsverletzung",
            "   V. Rechtswegerschöpfung (§ 90 Abs. 2 BVerfGG)",
            "   VI. Subsidiarität (allgemeiner Grundsatz)",
            "   VII. Beschwerdefrist (§ 93 BVerfGG): 1 Monat / 1 Jahr",
            "   VIII. Form (§ 23 BVerfGG)",
            "B. Begründetheit",
            "   — Grundrechtsprüfung (s. Schema Grundrechte)",
        ],
        "hinweise": "Subsidiaritätsprinzip und Rechtswegerschöpfung sind zwei verschiedene Dinge! Subsidiarität geht weiter: alle Möglichkeiten zur Abhilfe müssen ausgeschöpft sein.",
        "klassiker": ["Urteilsverfassungsbeschwerde", "Gesetzesverfassungsbeschwerde", "unmittelbare Betroffenheit bei Gesetzen"],
    },

    # ============================================================
    #  ZPO
    # ============================================================
    {
        "id": "zpo_klage",
        "title": "Zulässigkeit der Leistungsklage (ZPO)",
        "topic": "ZPO",
        "normen": ["§§ 12–37, 253, 256 ZPO"],
        "examensrelevanz": 2,
        "schema": [
            "I. Eröffnung des Zivilrechtswegs (§ 13 GVG)",
            "II. Zuständigkeit",
            "   1. Sachliche Zuständigkeit (§§ 23, 71 GVG)",
            "   2. Örtliche Zuständigkeit (§§ 12 ff. ZPO)",
            "      — Allgemeiner Gerichtsstand: §§ 13, 17 ZPO",
            "      — Besonderer Gerichtsstand: §§ 29, 32 ZPO",
            "      — Ausschließlicher Gerichtsstand: §§ 24, 29a ZPO",
            "III. Parteifähigkeit (§ 50 ZPO)",
            "IV. Prozessfähigkeit (§§ 51 f. ZPO)",
            "V. Ordnungsgemäße Klageerhebung (§ 253 ZPO)",
            "VI. Rechtsschutzbedürfnis",
            "VII. Keine anderweitige Rechtshängigkeit (§ 261 ZPO) / Rechtskraft",
        ],
        "hinweise": "ZPO-Klausuren oft als Teil der Zivilklausur. Sachliche Zuständigkeit: AG bis 5.000 €. Streitwert berechnen nicht vergessen. § 32 ZPO bei Delikt = deliktischer Handlungs-/Erfolgsort.",
        "klassiker": ["Gerichtsstandvereinbarung (§ 38 ZPO)", "Streitwert bei mehreren Ansprüchen", "Klage auf künftige Leistung § 259 ZPO"],
    },
]


def get_by_topic(topic: str) -> list[dict]:
    """Alle Schemata eines bestimmten Rechtsgebiets."""
    return [s for s in SCHEMAS if s["topic"] == topic]


def get_by_id(schema_id: str) -> dict | None:
    """Schema nach ID suchen."""
    return next((s for s in SCHEMAS if s["id"] == schema_id), None)


def get_all_topics() -> list[str]:
    """Alle vorhandenen Topics, sortiert."""
    return sorted({s["topic"] for s in SCHEMAS})


def search(query: str) -> list[dict]:
    """Einfache Volltextsuche über Titel, Normen und Hinweise."""
    q = query.lower()
    results = []
    for s in SCHEMAS:
        blob = (
            s["title"].lower()
            + " ".join(s["normen"]).lower()
            + s.get("hinweise", "").lower()
            + " ".join(s.get("klassiker", [])).lower()
        )
        if q in blob:
            results.append(s)
    return results
