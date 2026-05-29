"""XP · Level · Streak · Achievements — Gamification-System.

Levels (juristische Karrierestufen):
  1  Erstsemester         0
  2  Fortgeschrittener    200
  3  Übungsklausurenschreiber 500
  4  Repetitor-Kandidat   1 000
  5  AG-Veteran           2 000
  6  Klausurprofi         3 500
  7  Prüfungskandidat     5 500
  8  Examensvorbereiter   8 500
  9  Examinand           13 000
  10 Volljurist          20 000
"""
from __future__ import annotations

import datetime as dt
import time
from typing import Any

import streamlit as st

from src.github_db import read_json, write_json


# ── XP-Tabelle ──────────────────────────────────────────────
XP: dict[str, int] = {
    "card_easy":   15,
    "card_good":   10,
    "card_hard":    5,
    "card_again":   3,
    "correction":  50,
    "material":    20,
    "case":        15,
    "plan":        10,
    "oral_exam":   30,
    "login":        5,
    "schema":       8,
    "streit":      10,
    "handwriting": 25,
    "project":     20,
}

# ── Level-Definitionen ───────────────────────────────────────
LEVELS: list[tuple[int, str, str]] = [
    (0,     "Erstsemester",            "📘"),
    (200,   "Fortgeschrittener",        "📗"),
    (500,   "Übungsklausurenschreiber", "📙"),
    (1000,  "Repetitor-Kandidat",       "📕"),
    (2000,  "AG-Veteran",               "⚖️"),
    (3500,  "Klausurprofi",             "🔍"),
    (5500,  "Prüfungskandidat",         "🎯"),
    (8500,  "Examensvorbereiter",       "🏛️"),
    (13000, "Examinand",                "⚡"),
    (20000, "Volljurist",               "🎓"),
]

# ── Achievements ─────────────────────────────────────────────
ACHIEVEMENTS: list[dict] = [
    # Erste Schritte
    {"id": "first_login",     "icon": "🌅", "name": "Erster Tag",
     "desc": "Zum ersten Mal eingeloggt",          "xp": 10,  "check": lambda s: s.get("total_logins", 0) >= 1},
    {"id": "first_card",      "icon": "🎴", "name": "Erste Karte",
     "desc": "Erste Karteikarte gelernt",           "xp": 10,  "check": lambda s: s.get("stats", {}).get("cards_reviewed", 0) >= 1},
    {"id": "first_correction","icon": "✍️", "name": "Erster Rotstift",
     "desc": "Erste Klausur korrigiert",            "xp": 25,  "check": lambda s: s.get("stats", {}).get("corrections", 0) >= 1},
    {"id": "first_material",  "icon": "📤", "name": "Erster Upload",
     "desc": "Erstes Material hochgeladen",         "xp": 15,  "check": lambda s: s.get("stats", {}).get("materials_uploaded", 0) >= 1},
    # Streak-Achievements
    {"id": "streak_3",        "icon": "🔥", "name": "Drei Tage",
     "desc": "3 Tage in Folge gelernt",             "xp": 20,  "check": lambda s: s.get("streak", 0) >= 3},
    {"id": "streak_7",        "icon": "🔥🔥", "name": "Wochenmarathon",
     "desc": "7 Tage in Folge gelernt",             "xp": 50,  "check": lambda s: s.get("streak", 0) >= 7},
    {"id": "streak_30",       "icon": "💎", "name": "Monatsheld",
     "desc": "30 Tage in Folge gelernt",            "xp": 200, "check": lambda s: s.get("streak", 0) >= 30},
    # Karten-Achievements
    {"id": "cards_10",        "icon": "🃏", "name": "Lernstarter",
     "desc": "10 Karteikarten gelernt",             "xp": 15,  "check": lambda s: s.get("stats", {}).get("cards_reviewed", 0) >= 10},
    {"id": "cards_50",        "icon": "🎯", "name": "Ausdauer",
     "desc": "50 Karteikarten gelernt",             "xp": 40,  "check": lambda s: s.get("stats", {}).get("cards_reviewed", 0) >= 50},
    {"id": "cards_200",       "icon": "🏆", "name": "Kartenmeister",
     "desc": "200 Karteikarten gelernt",            "xp": 100, "check": lambda s: s.get("stats", {}).get("cards_reviewed", 0) >= 200},
    # Klausur-Achievements
    {"id": "corrections_5",   "icon": "⚖️", "name": "Korrekturbogen",
     "desc": "5 Klausuren korrigiert",              "xp": 50,  "check": lambda s: s.get("stats", {}).get("corrections", 0) >= 5},
    {"id": "corrections_20",  "icon": "🎓", "name": "Klausurprofi",
     "desc": "20 Klausuren korrigiert",             "xp": 150, "check": lambda s: s.get("stats", {}).get("corrections", 0) >= 20},
    # Prüfungs-Achievements
    {"id": "oral_5",          "icon": "🎤", "name": "Redegewandt",
     "desc": "5 mündliche Prüfungen absolviert",    "xp": 75,  "check": lambda s: s.get("stats", {}).get("oral_exams", 0) >= 5},
    # Level-Achievements
    {"id": "level_5",         "icon": "⚖️", "name": "AG-Veteran",
     "desc": "Level 5 erreicht",                    "xp": 100, "check": lambda s: get_level_info(s.get("xp", 0))["level"] >= 5},
    {"id": "level_10",        "icon": "🎓", "name": "Volljurist",
     "desc": "Maximales Level erreicht!",           "xp": 500, "check": lambda s: get_level_info(s.get("xp", 0))["level"] >= 10},
    # XP-Meilensteine
    {"id": "xp_500",          "icon": "⚡", "name": "Lernstart",
     "desc": "500 XP gesammelt",                    "xp": 25,  "check": lambda s: s.get("xp", 0) >= 500},
    {"id": "xp_2000",         "icon": "✨", "name": "Engagiert",
     "desc": "2.000 XP gesammelt",                  "xp": 50,  "check": lambda s: s.get("xp", 0) >= 2000},
    {"id": "xp_5000",         "icon": "🌟", "name": "Dediziert",
     "desc": "5.000 XP gesammelt",                  "xp": 100, "check": lambda s: s.get("xp", 0) >= 5000},
]


# ── Pfade ────────────────────────────────────────────────────

def _score_path() -> str:
    from src.config import personal_path
    return personal_path("score.json")


def _default() -> dict[str, Any]:
    return {
        "xp": 0, "streak": 0, "last_login": None,
        "total_logins": 0, "log": [],
        "unlocked_achievements": [],
        "stats": {
            "cards_reviewed": 0, "corrections": 0,
            "materials_uploaded": 0, "cases_generated": 0, "oral_exams": 0,
        },
    }


# ── Core API ─────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_score(_username: str) -> dict[str, Any]:
    data = read_json(_score_path(), default=None)
    if data is None:
        return _default()
    base = _default()
    base.update(data)
    return base


def _invalidate(_username: str) -> None:
    get_score.clear()


def _username() -> str:
    u = st.session_state.get("auth_user")
    return u["username"] if u else "default"


def award_xp(action: str, note: str = "") -> int:
    earned = XP.get(action, 0)
    if earned <= 0:
        return 0
    uname = _username()
    score = get_score(uname)
    score["xp"] = score.get("xp", 0) + earned
    stat_map = {
        "card_easy": "cards_reviewed", "card_good": "cards_reviewed",
        "card_hard": "cards_reviewed", "card_again": "cards_reviewed",
        "correction": "corrections", "material": "materials_uploaded",
        "case": "cases_generated", "oral_exam": "oral_exams",
    }
    if action in stat_map:
        k = stat_map[action]
        score["stats"][k] = score["stats"].get(k, 0) + 1
    score.setdefault("log", [])
    score["log"] = ([{"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                      "action": action, "xp": earned, "note": note}]
                    + score["log"])[:100]
    # Achievements prüfen
    new_ach = _check_achievements(score)
    for a in new_ach:
        score["xp"] += a["xp"]
        st.toast(f"🏆 Achievement: **{a['name']}** +{a['xp']} XP", icon="🏆")
    write_json(_score_path(), score, commit_msg=f"xp: +{earned} ({action})")
    _invalidate(uname)
    return earned


def check_and_award_login_streak() -> int:
    uname = _username()
    score = get_score(uname)
    today = dt.date.today().isoformat()
    if score.get("last_login") == today:
        return 0
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    score["streak"] = (score.get("streak", 0) + 1
                       if score.get("last_login") == yesterday else 1)
    score["last_login"] = today
    score["total_logins"] = score.get("total_logins", 0) + 1
    score["xp"] = score.get("xp", 0) + XP["login"]
    score.setdefault("log", [])
    score["log"] = ([{"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                      "action": "login", "xp": XP["login"],
                      "note": f"Streak {score['streak']}"}]
                    + score["log"])[:100]
    new_ach = _check_achievements(score)
    for a in new_ach:
        score["xp"] += a["xp"]
    write_json(_score_path(), score, commit_msg="daily login")
    _invalidate(uname)
    return XP["login"]


def _check_achievements(score: dict) -> list[dict]:
    unlocked = set(score.get("unlocked_achievements", []))
    new_ones = []
    for ach in ACHIEVEMENTS:
        if ach["id"] not in unlocked:
            try:
                if ach["check"](score):
                    unlocked.add(ach["id"])
                    new_ones.append(ach)
            except Exception:
                pass
    score["unlocked_achievements"] = list(unlocked)
    return new_ones


# ── Level-Logik ──────────────────────────────────────────────

def get_level_info(xp: int) -> dict[str, Any]:
    lvl_idx = 0
    for i, (thr, _, _) in enumerate(LEVELS):
        if xp >= thr:
            lvl_idx = i
    _, name, icon = LEVELS[lvl_idx]
    if lvl_idx < len(LEVELS) - 1:
        cur = LEVELS[lvl_idx][0]
        nxt = LEVELS[lvl_idx + 1][0]
        progress = min((xp - cur) / (nxt - cur), 1.0)
        to_next = nxt - xp
        next_name = LEVELS[lvl_idx + 1][1]
    else:
        progress, to_next, next_name = 1.0, 0, "Max"
    return {
        "level": lvl_idx + 1, "name": name, "icon": icon,
        "progress": progress, "xp_to_next": to_next,
        "next_name": next_name, "total_xp": xp,
    }


# ── Widget-HTML ──────────────────────────────────────────────

def render_score_widget(xp: int, streak: int) -> str:
    info = get_level_info(xp)
    pct = int(info["progress"] * 100)
    streak_html = (f'<span class="streak-badge">🔥 {streak} Tage</span>'
                   if streak >= 2 else "")
    return f"""
    <div style="display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:.4rem 0">
      <span class="xp-pill">{info['icon']} {xp:,} XP</span>
      <span class="lvl-badge">Lv.{info['level']} · {info['name']}</span>
      {streak_html}
    </div>
    <div style="font-size:.68rem;color:rgba(255,255,255,.4);
         font-family:'IBM Plex Sans',sans-serif;margin:.25rem 0 .15rem">
      {pct}% → Lv.{info['level']+1} {info['next_name']}
      {f'· noch {info["xp_to_next"]:,} XP' if info['xp_to_next'] else ''}
    </div>
    <div class="xp-track">
      <div class="xp-fill" style="width:{pct}%"></div>
    </div>"""


def render_achievements_grid(score: dict) -> None:
    """Rendert das Achievement-Grid in der UI."""
    unlocked = set(score.get("unlocked_achievements", []))
    total = len(ACHIEVEMENTS)
    done = len(unlocked)

    col_hdr, col_stat = st.columns([3, 1])
    with col_hdr:
        st.markdown(
            f'<div class="sec-hdr">🏆 Achievements · {done}/{total} freigeschaltet</div>',
            unsafe_allow_html=True,
        )
    with col_stat:
        st.progress(done / total if total else 0)

    cols = st.columns(3)
    for i, ach in enumerate(ACHIEVEMENTS):
        is_done = ach["id"] in unlocked
        locked_cls = "" if is_done else " locked"
        bg = "background:linear-gradient(135deg,#fefce8,#fef9c3)" if is_done else "background:white"
        border = "border:1.5px solid rgba(201,168,76,.4)" if is_done else "border:1px solid #f3f0e8"
        with cols[i % 3]:
            st.markdown(
                f'<div class="ach-card{locked_cls}" style="{bg};{border}">'
                f'<div class="ach-icon">{ach["icon"] if is_done else "🔒"}</div>'
                f'<div><div class="ach-name">{ach["name"]}</div>'
                f'<div class="ach-desc">{ach["desc"]}</div>'
                f'<div class="ach-xp">+{ach["xp"]} XP</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def show_xp_toast(earned: int, action_label: str = "") -> None:
    if earned > 0:
        suffix = f" — {action_label}" if action_label else ""
        st.toast(f"⚡ +{earned} XP{suffix}", icon="✨")
