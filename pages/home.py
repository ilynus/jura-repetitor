"""Tagesdashboard — Heute wichtig, To-do, Adaptive Lernvorschläge."""
from __future__ import annotations
import datetime as dt
import json
import streamlit as st
import streamlit.components.v1 as components

from src import srs
from src.auth import is_admin
from src.config import PATH_FLASHCARDS, PATH_SHARED_MATERIALS, PATH_TODO, personal_path
from src.github_db import read_json, write_json, now_iso
from src.llm import chat_complete
from src import personas
from src.score import ACHIEVEMENTS, get_level_info, get_score, render_achievements_grid
from src.theme import apply_theme, gold_divider, section_header, stat_card, nav_tile, render_top_bar

apply_theme()
user = st.session_state.get("auth_user", {"username":"default","display_name":"Nutzer","role":"user"})
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp", 0)
streak = score_data.get("streak", 0)
info = get_level_info(xp)

# ── TOP BAR ──────────────────────────────────────────────────
render_top_bar(user["display_name"], xp, info["name"], info["icon"])

# ── HEADER ───────────────────────────────────────────────────
col_h, col_clk = st.columns([3, 1])
with col_h:
    today = dt.date.today()
    weekdays = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    months = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    st.markdown(
        f"""<h1 style="margin-bottom:.05rem">Guten Tag, {user['display_name']} 👋</h1>
        <p style="font-family:'IBM Plex Sans',sans-serif;font-size:.88rem;color:#57534e;margin:0 0 .5rem">
        {weekdays[today.weekday()]}, {today.day}. {months[today.month-1]} {today.year} &nbsp;·&nbsp;
        <span style="color:#c9a84c">{info['icon']} Lv.{info['level']} · {info['name']}</span></p>""",
        unsafe_allow_html=True,
    )
with col_clk:
    st.markdown("<div style='margin-top:.4rem'></div>", unsafe_allow_html=True)
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400&display=swap" rel="stylesheet">
    <div style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:10px;
      padding:.45rem .85rem;border:1px solid rgba(201,168,76,.22);display:inline-block">
      <div id="ct" style="font-family:'IBM Plex Mono',monospace;font-size:1.35rem;
        font-weight:500;color:#e8c97b;letter-spacing:.04em">--:--:--</div>
      <div id="cd" style="font-family:'IBM Plex Sans',sans-serif;font-size:.7rem;
        color:rgba(255,255,255,.6);margin-top:.05rem">Laden...</div>
    </div>
    <script>
    const D=['So','Mo','Di','Mi','Do','Fr','Sa'];
    const M=['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
    function pad(n){return String(n).padStart(2,'0')}
    function tick(){
      var n=new Date();
      var t=document.getElementById('ct');var d=document.getElementById('cd');
      if(t)t.textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());
      if(d)d.textContent=D[n.getDay()]+', '+pad(n.getDate())+'. '+M[n.getMonth()]+' '+n.getFullYear();
    }
    tick();setInterval(tick,1000);
    </script>""", height=68, scrolling=False)

gold_divider()

# ── STATISTIK ────────────────────────────────────────────────
try:
    cards = read_json(PATH_FLASHCARDS(), default=[]) or []
    srs_s = srs.stats(cards)
    n_cards, n_due, n_learned = srs_s["total"], srs_s["due"], srs_s["learned"]
except Exception:
    n_cards = n_due = n_learned = 0

n_shared = len(read_json(PATH_SHARED_MATERIALS(), default=[]) or [])
stats_obj = score_data.get("stats", {})
n_corrections = stats_obj.get("corrections", 0)

c1,c2,c3,c4 = st.columns(4)
for col,(icon,num,lbl),d in zip([c1,c2,c3,c4],[
    ("📇",str(n_cards),"Karteikarten"),("⏰",str(n_due),"Heute fällig"),
    ("✅",str(n_learned),"Gefestigt"),("⚡",f"{xp:,}","XP gesamt")],[.05,.09,.13,.17]):
    with col: st.markdown(stat_card(icon,num,lbl,d), unsafe_allow_html=True)

st.markdown("<div style='margin:.4rem 0'></div>", unsafe_allow_html=True)
c5,c6,c7,c8 = st.columns(4)
for col,(icon,num,lbl),d in zip([c5,c6,c7,c8],[
    ("✍️",str(n_corrections),"Klausuren"),("🔥",str(streak) if streak else "–","Tage Streak"),
    ("🏆",str(len(score_data.get("unlocked_achievements",[]))),"Achievements"),
    ("🏛️",f"Lv.{info['level']}",info["name"])],[.21,.25,.29,.33]):
    with col: st.markdown(stat_card(icon,num,lbl,d), unsafe_allow_html=True)

if n_due > 0:
    st.markdown(
        f'<div style="margin:.5rem 0;display:flex;align-items:center;gap:.5rem">'
        f'<span class="due-dot"></span>'
        f'<span style="font-size:.82rem;font-weight:600;color:#d97706">'
        f'{n_due} Karte{"n" if n_due!=1 else ""} warten heute auf dich</span></div>',
        unsafe_allow_html=True,
    )

gold_divider()

# ── HAUPTBEREICH: 2 Spalten ───────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    # ── TO-DO LISTE ──────────────────────────────────────────
    section_header("✅", "Heutige Aufgaben")

    PATH_TODAY_TODO = lambda: personal_path("todo.json")
    todos = read_json(PATH_TODAY_TODO(), default=[]) or []

    # Neue Aufgabe
    with st.form("add_todo", clear_on_submit=True):
        cols_todo = st.columns([4, 1, 1])
        with cols_todo[0]:
            new_task = st.text_input("", placeholder="Neue Aufgabe...", label_visibility="collapsed")
        with cols_todo[1]:
            prio = st.selectbox("", ["🔴 Hoch","🟡 Mittel","🟢 Niedrig"],
                                label_visibility="collapsed", key="todo_prio")
        with cols_todo[2]:
            add_todo = st.form_submit_button("➕ Hinzufügen", use_container_width=True)
    if add_todo and new_task.strip():
        prio_map = {"🔴 Hoch":"high","🟡 Mittel":"med","🟢 Niedrig":"low"}
        todos.append({"id":now_iso(),"text":new_task.strip(),
                      "prio":prio_map.get(prio,"med"),"done":False,
                      "created":dt.date.today().isoformat()})
        write_json(PATH_TODAY_TODO(), todos, commit_msg="add todo")
        st.rerun()

    # Aufgaben anzeigen
    if not todos:
        st.caption("Keine Aufgaben — füge eine hinzu!")
    else:
        prio_css = {"high":"todo-prio-high","med":"todo-prio-med","low":"todo-prio-low"}
        for i, t in enumerate(todos):
            done_cls = " done" if t.get("done") else ""
            prio_cls = prio_css.get(t.get("prio","med"),"todo-prio-med")
            c_check, c_text, c_del = st.columns([1, 8, 1])
            with c_check:
                checked = st.checkbox("", value=t.get("done",False), key=f"todo_ck_{i}",
                                      label_visibility="collapsed")
                if checked != t.get("done",False):
                    todos[i]["done"] = checked
                    write_json(PATH_TODAY_TODO(), todos, commit_msg="todo update")
                    st.rerun()
            with c_text:
                st.markdown(
                    f'<div class="todo-item {prio_cls}{done_cls}" style="margin-bottom:0">'
                    f'{t["text"]}</div>', unsafe_allow_html=True)
            with c_del:
                if st.button("✕", key=f"todo_del_{i}"):
                    todos.pop(i)
                    write_json(PATH_TODAY_TODO(), todos, commit_msg="delete todo")
                    st.rerun()

        done_count = sum(1 for t in todos if t.get("done"))
        if todos:
            st.progress(done_count / len(todos),
                        text=f"{done_count}/{len(todos)} erledigt")

    # ── XP-FORTSCHRITT ───────────────────────────────────────
    st.markdown("<div style='margin-top:.75rem'></div>", unsafe_allow_html=True)
    section_header("🎮", "Lernfortschritt")
    pct = int(info["progress"] * 100)
    st.markdown(
        f"""<div style="background:white;border:1px solid #f0ede4;border-radius:10px;
        padding:.9rem 1.1rem;box-shadow:0 1px 3px rgba(26,39,68,.06)">
        <div style="display:flex;justify-content:space-between;margin-bottom:.4rem">
          <span style="font-family:'Playfair Display',serif;font-weight:600;
            color:#1a2744;font-size:.9rem">{info['icon']} Level {info['level']} · {info['name']}</span>
          <span style="font-family:'IBM Plex Mono',monospace;font-size:.78rem;
            color:#c9a84c;font-weight:600">{xp:,} XP</span>
        </div>
        <div style="background:#f0ede4;border-radius:99px;height:9px;overflow:hidden">
          <div style="width:{pct}%;height:100%;border-radius:99px;
            background:linear-gradient(90deg,#1a2744 0%,#c9a84c 100%);
            animation:growXP 1.2s cubic-bezier(.4,0,.2,1) both"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:.3rem">
          <span style="font-size:.68rem;color:#57534e">{pct}% bis Level {info['level']+1}</span>
          <span style="font-size:.68rem;color:#57534e">
            {'noch '+f'{info["xp_to_next"]:,} XP' if info['xp_to_next'] else '🎉 Max!'}</span>
        </div></div>""",
        unsafe_allow_html=True,
    )

with col_right:
    # ── ADAPTIVE LERNVORSCHLÄGE ───────────────────────────────
    section_header("🤖", "Heute empfohlen")

    adapt_key = f"adapt_{dt.date.today().isoformat()}_{uname}"
    if adapt_key not in st.session_state:
        if st.button("💡 KI-Vorschläge generieren", type="primary", use_container_width=True):
            profile = None
            try:
                from src.profile import get_profile
                profile = get_profile(uname)
            except Exception:
                pass

            weak = profile.get("schwache_rechtsgebiete",[]) if profile else []
            exam_date = profile.get("examenstermin","") if profile else ""
            prompt = (
                f"Ich lerne für das Staatsexamen.\n"
                f"Heute: {dt.date.today().isoformat()}\n"
                f"Karteikarten fällig: {n_due}\n"
                f"Korrekturen bisher: {n_corrections}\n"
                f"XP: {xp} (Level {info['level']})\n"
                f"Schwache Gebiete: {', '.join(weak) or 'unbekannt'}\n"
                f"Examenstermin: {exam_date or 'unbekannt'}\n\n"
                f"Gib mir 4 konkrete Lernempfehlungen für heute (je 1-2 Sätze). "
                f"Nummeriert, prägnant, examensorientiert."
            )
            with st.spinner("Analysiere deinen Lernstand..."):
                suggestions = chat_complete(
                    messages=[{"role":"user","content":prompt}],
                    system_prompt=personas.LERNCOACH,
                )
            st.session_state[adapt_key] = suggestions
            st.rerun()
    else:
        st.markdown(
            f'<div style="background:white;border:1px solid #f0ede4;border-radius:10px;'
            f'padding:.9rem 1.1rem;box-shadow:0 1px 3px rgba(26,39,68,.06);'
            f'font-family:\'IBM Plex Sans\',sans-serif;font-size:.83rem;'
            f'color:#292524;line-height:1.6">{st.session_state[adapt_key]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("🔄 Neu generieren", key="regen_adapt"):
            del st.session_state[adapt_key]
            st.rerun()

    st.markdown("<div style='margin-top:.6rem'></div>", unsafe_allow_html=True)

    # ── LETZTE AKTIVITÄTEN ────────────────────────────────────
    section_header("📈", "Letzte Aktivitäten")
    log = score_data.get("log", [])
    ACTION_LABELS = {
        "card_easy":"🎴 Karte — Einfach","card_good":"🎴 Karte — Gut",
        "card_hard":"🎴 Karte — Schwer","card_again":"🎴 Karte — Nochmal",
        "correction":"✍️ Klausur","material":"📤 Upload","case":"📋 Fall",
        "plan":"📅 Plan","oral_exam":"🎤 Mündlich","login":"☀️ Login",
        "schema":"🗂️ Schema","streit":"⚔️ Streitstand",
        "handwriting":"✏️ Handschrift","project":"📂 Projekt",
    }
    if not log:
        st.caption("Noch keine Aktivitäten.")
    else:
        # Schema-Einträge zusammenfassen damit Log nicht vollläuft
        non_schema = [e for e in log if e.get("action") != "schema"]
        schema_entries = [e for e in log if e.get("action") == "schema"]
        display_log = non_schema[:7]
        if schema_entries:
            total_schema_xp = sum(e.get("xp",0) for e in schema_entries)
            display_log.append({
                "action": "schema",
                "ts": schema_entries[0].get("ts",""),
                "xp": total_schema_xp,
                "_label": f"🗂️ {len(schema_entries)} Schemata angesehen",
            })
        for entry in display_log:
            ts = entry.get("ts","")[:16].replace("T"," ")
            label = entry.get("_label") or ACTION_LABELS.get(entry.get("action","?"), "?")
            xp_e = entry.get("xp",0)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:.28rem 0;border-bottom:1px solid #f0ede4;'
                f'font-family:\'IBM Plex Sans\',sans-serif;font-size:.81rem">'
                f'<span style="color:#292524;font-weight:500">{label}</span>'
                f'<span style="display:flex;gap:.4rem;align-items:center">'
                f'<span style="color:#57534e;font-size:.72rem">{ts}</span>'
                f'<span style="background:#1a2744;color:#e8c97b;padding:.1rem .45rem;'
                f'border-radius:99px;font-family:\'IBM Plex Mono\',monospace;'
                f'font-size:.7rem;font-weight:600">+{xp_e}</span>'
                f'</span></div>',
                unsafe_allow_html=True,
            )

gold_divider()

# ── ACHIEVEMENTS ─────────────────────────────────────────────
with st.expander("🏆 Achievements", expanded=False):
    render_achievements_grid(score_data)
