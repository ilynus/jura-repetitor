"""Examensbegleiter — Navigation."""
from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="Examensbegleiter", page_icon="🎓",
    layout="wide", initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/home.py",                 title="Heute",             icon="🏠", default=True),
    st.Page("pages/lernen.py",               title="Lernen",            icon="📚"),
    st.Page("pages/klausur_pruefung.py",     title="Klausur & Prüfung", icon="✍️"),
    st.Page("pages/materialien_projekte.py", title="Materialien",       icon="📂"),
    st.Page("pages/planung_quellen.py",      title="Planung & Quellen", icon="🗓️"),
    st.Page("pages/profil.py",               title="Profil",            icon="⚙️"),
], position="sidebar")

# Imports nach set_page_config
from src.auth import logout, require_login
from src.bug_reporter import save_bug_report
from src.config import MODEL_DEFAULT, MODEL_HEAVY
from src.profile import is_onboarding_done, render_onboarding
from src.score import (check_and_award_login_streak, get_level_info,
                       get_score, render_score_widget, show_xp_toast)
from src.theme import apply_theme

apply_theme()
user = require_login()
uname = user["username"]

if not is_onboarding_done(uname):
    done = render_onboarding(uname)
    if not done:
        st.stop()
    st.rerun()

earned = check_and_award_login_streak()
if earned > 0:
    show_xp_toast(earned, "Tages-Login")

score_data = get_score(uname)
xp = int(score_data.get("xp", 0))
streak = int(score_data.get("streak", 0))
info = get_level_info(xp)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""<div style="padding:.4rem 0 .2rem">
        <div style="font-family:'Playfair Display',serif;font-size:.98rem;
          font-weight:700;color:rgba(255,255,255,.95)">🎓 Examensbegleiter</div>
        <div style="font-size:.65rem;color:rgba(255,255,255,.55);margin-top:.1rem">
          Juristisches Staatsexamen</div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div style="background:rgba(255,255,255,.07);
          border:1px solid rgba(255,255,255,.15);border-radius:8px;
          padding:.5rem .85rem;margin:.3rem 0 .45rem">
          <div style="font-weight:600;font-size:.85rem;color:rgba(255,255,255,.95)">
            {'🛡️' if user['role']=='admin' else '👤'} {user['display_name']}</div>
          <div style="font-size:.67rem;color:rgba(255,255,255,.55);
            font-family:'IBM Plex Mono',monospace;margin-top:.1rem">
            @{user['username']}</div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(render_score_widget(xp, streak), unsafe_allow_html=True)
    st.markdown("<div style='margin:.35rem 0'></div>", unsafe_allow_html=True)

    if st.button("🚪 Abmelden", use_container_width=True):
        logout()

    st.divider()
    st.markdown(
        f"""<div style="font-size:.62rem;color:rgba(255,255,255,.45);
          font-family:'IBM Plex Mono',monospace;line-height:1.85">
          Chat: <span style="color:rgba(201,168,76,.7)">{MODEL_DEFAULT}</span><br>
          Korrektor: <span style="color:rgba(201,168,76,.7)">{MODEL_HEAVY}</span><br>
          ✨ Caching · Haiku für JSON</div>""",
        unsafe_allow_html=True,
    )

    st.divider()
    with st.expander("🐛 Bug melden"):
        bug_typ = st.selectbox(
            "Typ",
            ["🐛 Bug / Fehler", "✨ Verbesserung", "💡 Feature", "❓ Frage"],
            key="sb_bug_typ",
            label_visibility="collapsed",
        )
        bug_txt = st.text_area(
            "Beschreibung",
            height=75,
            key="sb_bug_txt",
            placeholder="Was ist passiert?\nWelche Seite?",
            label_visibility="collapsed",
        )
        if st.button("📤 Senden", key="sb_bug_send", use_container_width=True):
            if bug_txt.strip():
                save_bug_report(bug_typ, bug_txt, user=uname)
                st.success("✅ Danke!")

pg.run()
