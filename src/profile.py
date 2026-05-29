"""Nutzerprofil — Onboarding, Speicherung, Prompt-Injection.

Das Profil wird einmalig beim ersten Login erfasst und kann jederzeit
aktualisiert werden. Es wird in jeden LLM-Aufruf als Kontext eingebunden,
sodass Claude den Nutzer von Anfang an kennt.
"""
from __future__ import annotations
from typing import Any
import streamlit as st
from src.github_db import read_json, write_json
from src.config import personal_path


# ── Pfad ─────────────────────────────────────────────────────

def _profile_path() -> str:
    return personal_path("profile.json")


# ── Default ──────────────────────────────────────────────────

def _default() -> dict[str, Any]:
    return {
        "completed": False,
        "universitaet": "",
        "studienort": "",
        "fachsemester": "",
        "examenstyp": "1. Staatsexamen (Universität)",
        "bundesland": "Nordrhein-Westfalen",
        "examenstermin": "",
        "schwerpunktbereich": "",
        "schwache_rechtsgebiete": [],
        "starke_rechtsgebiete": [],
        "lernstil": "",
        "ziel_punkte": "10",
        "woechentliche_lernstunden": "",
        "berufstaetig": False,
        "notizen": "",
    }


# ── API ───────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_profile(_username: str) -> dict[str, Any]:
    data = read_json(_profile_path(), default=None)
    if data is None:
        return _default()
    base = _default()
    base.update(data)
    return base


def save_profile(profile: dict) -> bool:
    profile["completed"] = True
    ok = write_json(_profile_path(), profile, commit_msg="update user profile")
    get_profile.clear()
    return ok


def is_onboarding_done(_username: str) -> bool:
    return get_profile(_username).get("completed", False)


# ── Prompt-Injection ─────────────────────────────────────────

def build_profile_context(username: str) -> str:
    """Gibt einen Profilblock zurück, der in jeden System-Prompt eingefügt wird."""
    p = get_profile(username)
    if not p.get("completed"):
        return ""

    lines = ["---", "# NUTZERPROFIL (immer berücksichtigen)", ""]

    if p.get("universitaet"):
        lines.append(f"**Universität:** {p['universitaet']}")
    if p.get("studienort"):
        lines.append(f"**Studienort:** {p['studienort']}")
    if p.get("fachsemester"):
        lines.append(f"**Fachsemester:** {p['fachsemester']}")
    if p.get("examenstyp"):
        lines.append(f"**Examensziel:** {p['examenstyp']}")
    if p.get("bundesland"):
        lines.append(f"**Bundesland:** {p['bundesland']}")
    if p.get("examenstermin"):
        lines.append(f"**Geplanter Examenstermin:** {p['examenstermin']}")
    if p.get("schwerpunktbereich"):
        lines.append(f"**Schwerpunktbereich:** {p['schwerpunktbereich']}")
    if p.get("schwache_rechtsgebiete"):
        lines.append(f"**Schwache Rechtsgebiete (besonders fördern):** "
                     f"{', '.join(p['schwache_rechtsgebiete'])}")
    if p.get("starke_rechtsgebiete"):
        lines.append(f"**Starke Rechtsgebiete:** "
                     f"{', '.join(p['starke_rechtsgebiete'])}")
    if p.get("lernstil"):
        lines.append(f"**Lernstil:** {p['lernstil']}")
    if p.get("ziel_punkte"):
        lines.append(f"**Zielpunktzahl im Examen:** {p['ziel_punkte']} Punkte")
    if p.get("woechentliche_lernstunden"):
        lines.append(f"**Verfügbare Lernzeit:** ca. {p['woechentliche_lernstunden']} Stunden/Woche")
    if p.get("berufstaetig"):
        lines.append("**Nebentätigkeit:** Ja (bitte Lernpläne entsprechend anpassen)")
    if p.get("notizen"):
        lines.append(f"**Besondere Hinweise:** {p['notizen']}")

    lines += [
        "",
        "**Anweisungen zur Nutzung dieses Profils:**",
        "- Passe Erklärungen an den Studienort und das Fachsemester an.",
        "- Priorisiere bei Lernplänen die schwachen Rechtsgebiete.",
        "- Richte Klausurtraining auf die Zielpunktzahl aus.",
        "- Wenn Examenstermin gesetzt: Zeitplan darauf ausrichten.",
    ]

    return "\n".join(lines)


# ── Onboarding-UI ─────────────────────────────────────────────

RECHTSGEBIETE = [
    "BGB AT", "Schuldrecht AT", "Schuldrecht BT", "Sachenrecht",
    "Familienrecht", "Erbrecht", "HGB/Gesellschaftsrecht", "Arbeitsrecht", "ZPO",
    "Staatsorganisationsrecht", "Grundrechte", "Allg. Verwaltungsrecht",
    "Verwaltungsprozessrecht", "Polizei-/Ordnungsrecht NRW",
    "Kommunalrecht NRW", "Baurecht", "Europarecht", "Staatshaftungsrecht",
    "Strafrecht AT", "Strafrecht BT", "Strafprozessrecht",
]

SCHWERPUNKTE = [
    "Zivilrechtspflege / Wirtschaft",
    "Kriminalwissenschaften",
    "Öffentliches Recht / Staatswissenschaften",
    "Internationales Recht / Europarecht",
    "Arbeit und Soziales",
    "Steuerrecht",
    "Medizin- und Gesundheitsrecht",
    "Umwelt- und Planungsrecht",
    "Informations- und Medienrecht",
    "Sonstiger Schwerpunkt",
    "Kein Schwerpunktbereich",
]


def render_onboarding(username: str) -> bool:
    """Zeigt den Onboarding-Wizard. Gibt True zurück wenn abgeschlossen."""
    st.markdown("""
    <style>
    .onb-card {
      background: white;
      border: 1px solid #f3f0e8;
      border-radius: 14px;
      padding: 2rem 2.5rem;
      box-shadow: 0 4px 24px rgba(26,39,68,.09);
      max-width: 720px;
      margin: 0 auto;
    }
    .onb-step {
      background: linear-gradient(135deg,#1a2744,#243460);
      color: #e8c97b !important;
      font-family: 'IBM Plex Mono', monospace;
      font-size: .75rem; font-weight: 600;
      padding: .25rem .7rem; border-radius: 99px;
      display: inline-block; margin-bottom: .75rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Fortschritts-Header
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 .5rem">
      <div style="font-family:'Playfair Display',serif;font-size:2rem;
           font-weight:700;color:#1a2744">🎓 Willkommen!</div>
      <div style="font-family:'IBM Plex Sans',sans-serif;font-size:.95rem;
           color:#78716c;margin-top:.4rem">
        Lass uns dein Profil einrichten — damit der Examensbegleiter<br>
        von Anfang an auf dich zugeschnitten ist.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(0.0, text="Schritt 1 von 1 — dauert ~2 Minuten")
    st.markdown("<br>", unsafe_allow_html=True)

    profile = _default()

    with st.form("onboarding_form"):

        # ── Block 1: Studium ──────────────────────────────────
        st.markdown('<div class="onb-step">📚 Studium</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            profile["universitaet"] = st.text_input(
                "Universität *",
                value="Universität Münster",
                placeholder="Universität Münster",
            )
            profile["studienort"] = st.text_input(
                "Studienort *",
                value="Münster",
                placeholder="Münster",
            )
        with col2:
            profile["fachsemester"] = st.selectbox(
                "Fachsemester *",
                ["1. Semester", "2. Semester", "3. Semester", "4. Semester",
                 "5. Semester", "6. Semester", "7. Semester", "8. Semester",
                 "9. Semester", "10+ Semester", "Repetitor (kein Studium mehr)"],
                index=7,
            )
            profile["bundesland"] = st.selectbox(
                "Bundesland (für Landesrecht) *",
                ["Nordrhein-Westfalen", "Bayern", "Baden-Württemberg",
                 "Berlin", "Hamburg", "Hessen", "Niedersachsen",
                 "Rheinland-Pfalz", "Sachsen", "Anderes"],
                index=0,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Block 2: Examen ───────────────────────────────────
        st.markdown('<div class="onb-step">🏛️ Examen</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            profile["examenstyp"] = st.radio(
                "Welches Examen bereitest du vor? *",
                ["1. Staatsexamen (Universität)", "2. Staatsexamen (Referendariat)",
                 "Beide", "Noch unentschieden"],
                horizontal=False,
            )
        with col4:
            profile["examenstermin"] = st.text_input(
                "Geplanter Examenstermin (optional)",
                placeholder="z.B. Frühjahr 2026 oder 03/2026",
            )
            profile["ziel_punkte"] = st.select_slider(
                "Zielpunktzahl *",
                options=["6", "7", "8", "9", "10", "11", "12",
                         "13", "14", "15", "16", "17", "18"],
                value="10",
                help="Vollbefriedigend = 10–12 Punkte",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Block 3: Schwerpunkt ──────────────────────────────
        st.markdown('<div class="onb-step">🔬 Schwerpunktbereich</div>', unsafe_allow_html=True)
        profile["schwerpunktbereich"] = st.selectbox(
            "Schwerpunktbereich (falls Uni Münster)",
            ["Noch nicht gewählt"] + SCHWERPUNKTE,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Block 4: Stärken & Schwächen ─────────────────────
        st.markdown('<div class="onb-step">📊 Stärken & Schwächen</div>', unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        with col5:
            profile["schwache_rechtsgebiete"] = st.multiselect(
                "Schwache Rechtsgebiete 😟",
                RECHTSGEBIETE,
                help="Diese werden in Lernplänen priorisiert.",
            )
        with col6:
            profile["starke_rechtsgebiete"] = st.multiselect(
                "Starke Rechtsgebiete 💪",
                RECHTSGEBIETE,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Block 5: Lernstil & Zeit ──────────────────────────
        st.markdown('<div class="onb-step">⏱️ Lernstil & Zeit</div>', unsafe_allow_html=True)
        col7, col8 = st.columns(2)
        with col7:
            profile["lernstil"] = st.selectbox(
                "Wie lernst du am liebsten?",
                ["Gemischt (Theorie + Fälle)",
                 "Viel Falllösen, wenig Theorie",
                 "Erst Theorie, dann Fälle",
                 "Karteikarten-fokussiert",
                 "Klausuren schreiben und korrigieren"],
            )
            profile["woechentliche_lernstunden"] = st.selectbox(
                "Lernzeit pro Woche (durchschnittlich)",
                ["< 10 Stunden", "10–20 Stunden", "20–30 Stunden",
                 "30–40 Stunden", "40–50 Stunden", "> 50 Stunden (Vollzeit)"],
                index=2,
            )
        with col8:
            profile["berufstaetig"] = st.checkbox(
                "Ich bin neben dem Studium/Repetitorium berufstätig",
                help="Beeinflusst Lernpläne und Wochenstruktur.",
            )
            profile["notizen"] = st.text_area(
                "Besondere Hinweise für den Examensbegleiter (optional)",
                placeholder="z.B. 'Ich habe das Examen bereits einmal nicht bestanden', "
                            "'Ich repetiere bei Alpmann Schmidt', "
                            "'Schwerpunkt liegt auf ÖR'",
                height=100,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "✅ Profil speichern & loslegen",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not profile["universitaet"].strip():
            st.error("Bitte mindestens die Universität angeben.")
            return False
        with st.spinner("Speichere Profil..."):
            ok = save_profile(profile)
        if ok:
            st.success("🎉 Profil gespeichert! Du kannst jetzt loslegen.")
            st.balloons()
            return True
        else:
            st.error("Speichern fehlgeschlagen — GitHub-Verbindung prüfen.")
            return False

    return False


def render_profile_editor(username: str) -> None:
    """Einstellungsseite zum Bearbeiten des Profils."""
    p = get_profile(username)

    st.subheader("👤 Mein Profil")
    st.caption("Diese Informationen fließen in alle KI-Antworten ein.")

    with st.form("profile_edit"):
        col1, col2 = st.columns(2)
        with col1:
            p["universitaet"] = st.text_input("Universität", value=p.get("universitaet",""))
            p["studienort"] = st.text_input("Studienort", value=p.get("studienort",""))
            p["fachsemester"] = st.text_input("Fachsemester", value=p.get("fachsemester",""))
            p["examenstermin"] = st.text_input("Examenstermin", value=p.get("examenstermin",""))
        with col2:
            p["examenstyp"] = st.selectbox("Examenstyp",
                ["1. Staatsexamen (Universität)","2. Staatsexamen (Referendariat)","Beide","Noch unentschieden"],
                index=["1. Staatsexamen (Universität)","2. Staatsexamen (Referendariat)","Beide","Noch unentschieden"].index(
                    p.get("examenstyp","1. Staatsexamen (Universität)")),
            )
            p["bundesland"] = st.text_input("Bundesland", value=p.get("bundesland","Nordrhein-Westfalen"))
            p["ziel_punkte"] = st.select_slider("Zielpunktzahl",
                options=["6","7","8","9","10","11","12","13","14","15","16","17","18"],
                value=p.get("ziel_punkte","10"),
            )
            p["woechentliche_lernstunden"] = st.text_input(
                "Lernstunden/Woche", value=p.get("woechentliche_lernstunden",""))

        p["schwerpunktbereich"] = st.text_input(
            "Schwerpunktbereich", value=p.get("schwerpunktbereich",""))
        p["schwache_rechtsgebiete"] = st.multiselect(
            "Schwache Rechtsgebiete", RECHTSGEBIETE,
            default=[r for r in p.get("schwache_rechtsgebiete",[]) if r in RECHTSGEBIETE])
        p["starke_rechtsgebiete"] = st.multiselect(
            "Starke Rechtsgebiete", RECHTSGEBIETE,
            default=[r for r in p.get("starke_rechtsgebiete",[]) if r in RECHTSGEBIETE])
        p["berufstaetig"] = st.checkbox("Berufstätig", value=p.get("berufstaetig", False))
        p["notizen"] = st.text_area("Besondere Hinweise", value=p.get("notizen",""), height=80)

        if st.form_submit_button("💾 Speichern", type="primary"):
            if save_profile(p):
                st.success("✅ Profil aktualisiert.")
            else:
                st.error("Speichern fehlgeschlagen.")

    # Profil-Vorschau
    with st.expander("👁️ So sieht Claude dein Profil"):
        ctx = build_profile_context(username)
        st.code(ctx, language="markdown")
