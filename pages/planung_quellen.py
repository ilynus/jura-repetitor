"""Planung & Quellen — Fokus-Modus, KI-Lernplanung, Lerncoach, Quellen, Rechtsprechung."""
from __future__ import annotations
import datetime as dt
import streamlit as st
import streamlit.components.v1 as components

from src import personas
from src.auth import require_login
from src.config import PATH_FOCUS, VERIFIED_SOURCES, personal_path
from src.github_db import read_json, write_json, now_iso
from src.legal_news import DEFAULT_FEEDS, LTO_FEEDS, fetch_all_lto_news, is_exam_relevant
from src.llm import chat_complete, chat_stream
from src.profile import get_profile
from src.score import award_xp, get_level_info, get_score, show_xp_toast
from src.theme import apply_theme, gold_divider, page_header, render_top_bar
from src.verified_sources import fetch_clean_text, is_verified

apply_theme()
user = require_login()
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp", 0)
info = get_level_info(xp)
render_top_bar(user["display_name"], xp, info["name"], info["icon"])
page_header("Planung & Quellen", "Fokus-Modus · KI-Lernplanung · Lerncoach · Quellen-Lookup · Rechtsprechung & News", "🗓️")

TABS = st.tabs(["🎯 Fokus-Modus", "🤖 KI-Lernplanung", "📅 Lerncoach", "🔍 Quellen-Lookup", "⚖️ News"])

# ════════════════════════════════════════════════════════════════
# TAB 1: FOKUS-MODUS
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    st.markdown("### 🎯 Fokus-Modus")
    st.caption("Pomodoro-Timer · Ablenkungsfrei · Tages-Fokusthema · Sitzungs-Tracking")

    profile = get_profile(uname)
    weak = profile.get("schwache_rechtsgebiete", [])

    col_cfg, col_timer = st.columns([1, 2])
    with col_cfg:
        focus_topic = st.text_input("Heutiges Fokus-Thema",
            value=weak[0] if weak else "", placeholder="z.B. § 280 BGB, Notwehr")
        pomo_work = st.select_slider("Arbeitszeit (Min)", [15, 20, 25, 30, 45, 50], 25)
        pomo_break = st.select_slider("Pause (Min)", [5, 10, 15], 5)
        pomo_rounds = st.slider("Runden", 1, 8, 4)

    with col_timer:
        focus_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@500;600&display=swap" rel="stylesheet">
        <div id="pomo-wrap" style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:14px;
          padding:2rem;text-align:center;border:1px solid rgba(201,168,76,.25);box-shadow:0 4px 20px rgba(26,39,68,.2)">
          <div id="pomo-label" style="font-family:'IBM Plex Sans',sans-serif;font-size:.85rem;
            font-weight:600;color:rgba(255,255,255,.7);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.5rem">
            FOKUS</div>
          <div id="pomo-time" style="font-family:'IBM Plex Mono',monospace;font-size:3.5rem;
            font-weight:500;color:#e8c97b;letter-spacing:.05em">{pomo_work:02d}:00</div>
          <div id="pomo-topic" style="font-family:'IBM Plex Sans',sans-serif;font-size:.82rem;
            color:rgba(255,255,255,.6);margin:.5rem 0 1.2rem">{focus_topic or "Kein Thema gesetzt"}</div>
          <div style="display:flex;gap:.75rem;justify-content:center">
            <button onclick="startPomo()" id="btn-start" style="background:rgba(201,168,76,.2);border:1px solid rgba(201,168,76,.4);
              color:#e8c97b;border-radius:8px;padding:.45rem 1.2rem;cursor:pointer;font-family:'IBM Plex Sans',sans-serif;font-weight:600">
              ▶ Start</button>
            <button onclick="pausePomo()" style="background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);
              color:rgba(255,255,255,.8);border-radius:8px;padding:.45rem 1.2rem;cursor:pointer;font-family:'IBM Plex Sans',sans-serif">
              ⏸ Pause</button>
            <button onclick="resetPomo()" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
              color:rgba(255,255,255,.6);border-radius:8px;padding:.45rem 1.2rem;cursor:pointer;font-family:'IBM Plex Sans',sans-serif">
              ↺ Reset</button>
          </div>
          <div id="pomo-rounds" style="margin-top:1rem;font-family:'IBM Plex Sans',sans-serif;
            font-size:.78rem;color:rgba(255,255,255,.45)">Runde 1 / {pomo_rounds}</div>
        </div>
        <script>
        var workMin={pomo_work},breakMin={pomo_break},totalRounds={pomo_rounds};
        var remaining=workMin*60,isRunning=false,isBreak=false,round=1,interval=null;
        function pad(n){{return String(n).padStart(2,'0')}}
        function updateDisplay(){{
          var m=Math.floor(remaining/60),s=remaining%60;
          document.getElementById('pomo-time').textContent=pad(m)+':'+pad(s);
          document.getElementById('pomo-label').textContent=isBreak?'PAUSE':'FOKUS';
          document.getElementById('pomo-rounds').textContent='Runde '+round+' / {pomo_rounds}';
          document.getElementById('pomo-time').style.color=isBreak?'#86efac':'#e8c97b';
        }}
        function startPomo(){{
          if(isRunning)return;
          isRunning=true;
          interval=setInterval(function(){{
            if(remaining>0){{remaining--;updateDisplay();}}
            else{{
              clearInterval(interval);isRunning=false;
              if(!isBreak){{isBreak=true;remaining=breakMin*60;}}
              else{{isBreak=false;round++;if(round>{pomo_rounds}){{round={pomo_rounds};alert('Alle Runden abgeschlossen! 🎉');return;}}remaining=workMin*60;}}
              updateDisplay();
            }}
          }},1000);
        }}
        function pausePomo(){{clearInterval(interval);isRunning=false;}}
        function resetPomo(){{clearInterval(interval);isRunning=false;isBreak=false;round=1;remaining=workMin*60;updateDisplay();}}
        updateDisplay();
        </script>"""
        components.html(focus_html, height=300, scrolling=False)

    gold_divider()
    st.markdown("#### 📊 Heutige Fokus-Sitzungen")
    focus_data = read_json(PATH_FOCUS(), default={"sessions":[]}) or {"sessions":[]}
    today_str = dt.date.today().isoformat()
    today_sessions = [s for s in focus_data.get("sessions",[]) if s.get("date") == today_str]

    col_log, col_add = st.columns([3,1])
    with col_add:
        if st.button("✅ Sitzung erfassen", type="primary", use_container_width=True):
            focus_data.setdefault("sessions",[]).append({
                "date": today_str, "topic": focus_topic or "Unbekannt",
                "duration": pomo_work, "ts": now_iso()
            })
            write_json(PATH_FOCUS(), focus_data, commit_msg=f"focus: {focus_topic}")
            award_xp("plan", note=f"Fokus: {focus_topic}")
            st.success("✅ Gespeichert!"); st.rerun()
    with col_log:
        if today_sessions:
            total_min = sum(s.get("duration",0) for s in today_sessions)
            st.markdown(f"**{len(today_sessions)} Sitzungen heute · {total_min} Minuten**")
            for s in today_sessions:
                st.markdown(
                    f'<div style="background:white;border:1px solid #f0ede4;border-radius:8px;'
                    f'padding:.4rem .75rem;margin-bottom:.25rem;font-size:.81rem;color:#292524">'
                    f'⏱️ {s.get("duration","?")} Min · {s.get("topic","?")}</div>',
                    unsafe_allow_html=True)
        else:
            st.caption("Noch keine Sitzungen heute. Starte den Timer!")

# ════════════════════════════════════════════════════════════════
# TAB 2: KI-LERNPLANUNG
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    st.markdown("### 🤖 KI-Lernplanung")
    st.caption("Adaptiver KI-Lernplan basierend auf deinem Profil, Fortschritt und Examenstermin.")
    profile = get_profile(uname)

    with st.form("lernplan_form"):
        col1,col2 = st.columns(2)
        with col1:
            plan_typ = st.selectbox("Plantyp", ["Wochenplan","Monatsplan","Examensgesamtplan","Intensivplan (2 Wochen vor Examen)"])
            verfuegbar = st.select_slider("Lernstunden/Tag", [1,2,3,4,5,6,7,8,9,10], 4)
        with col2:
            exam_datum = st.text_input("Examenstermin", value=profile.get("examenstermin",""), placeholder="z.B. März 2026")
            spez_wunsch = st.text_input("Besonderer Wunsch", placeholder="z.B. Schwerpunkt Sachenrecht diese Woche")
        gebiete_options = ["BGB AT","SchuldR AT","SchuldR BT","SachenR","FamR","ErbR",
                           "StrafR AT","StrafR BT","StPO","GR","AllgVerwR","VerwProzR","PolR","ZPO","HGB","EuR"]
        # Nur Werte als default die auch in der Options-Liste sind
        saved_weak = [g for g in profile.get("schwache_rechtsgebiete", []) if g in gebiete_options]
        weak_areas = st.multiselect("Schwache Gebiete (priorisieren)", gebiete_options, default=saved_weak[:5])
        berufstaetig = st.checkbox("Berufstätig", value=profile.get("berufstaetig", False))
        generate = st.form_submit_button("📅 Lernplan generieren", type="primary", use_container_width=True)

    if generate:
        stats = score_data.get("stats",{})
        prompt = (
            f"Erstelle einen {plan_typ} für das juristische Staatsexamen.\n\n"
            f"Nutzer-Profil:\n"
            f"- Examenstermin: {exam_datum or 'unbekannt'}\n"
            f"- Verfügbare Stunden: {verfuegbar}h/Tag{', berufstätig' if berufstaetig else ''}\n"
            f"- Schwache Gebiete (Priorität): {', '.join(weak_areas) or 'unbekannt'}\n"
            f"- Bisherige Korrekturen: {stats.get('corrections',0)}\n"
            f"- XP/Level: {xp} XP, Level {info['level']}\n"
            + (f"- Besonderer Wunsch: {spez_wunsch}\n" if spez_wunsch else "")
            + f"\nErstelle einen konkreten, realistischen {plan_typ} mit:\n"
            f"- Tagesgenaue Einteilung mit Themen und Zeiten\n"
            f"- Wiederholungszyklen (Spaced Repetition)\n"
            f"- Klausuranteil (mindestens 30%)\n"
            f"- Pufferzeit und Notfalltage\n"
            f"- Meilensteine und Checkpoints\n"
            f"Priorisierung nach Examensrelevanz."
        )
        with st.spinner("Generiere Lernplan..."):
            result = chat_complete([{"role":"user","content":prompt}], personas.LERNCOACH, max_tokens=3000)

        st.markdown("## 📅 Dein Lernplan")
        st.markdown(result)
        ts = now_iso()
        PATH_PLANS = lambda: personal_path("learning_plans.json")
        plans = read_json(PATH_PLANS(), default=[]) or []
        plans.append({"timestamp":ts,"typ":plan_typ,"plan":result})
        write_json(PATH_PLANS(), plans, commit_msg=f"learning plan: {plan_typ}")
        award_xp("plan", note=plan_typ)
        st.download_button("⬇️ Plan herunterladen", result, f"lernplan_{ts}.md", "text/markdown")
        st.success("✅ Plan gespeichert.")

    # Gespeicherte Pläne
    PATH_PLANS = lambda: personal_path("learning_plans.json")
    saved_plans = read_json(PATH_PLANS(), default=[]) or []
    if saved_plans:
        st.divider()
        with st.expander(f"📂 Gespeicherte Lernpläne ({len(saved_plans)})"):
            for p in reversed(saved_plans):
                with st.expander(f"📅 {p.get('typ','?')} · {p.get('timestamp','?')[:10]}"):
                    st.markdown(p.get("plan",""))

# ════════════════════════════════════════════════════════════════
# TAB 3: LERNCOACH
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    st.markdown("### 📅 Lerncoach")
    st.caption("Interaktiver Coach für Lernstrategie, Zeitplanung und Prüfungsvorbereitung.")
    if "lerncoach_msgs" not in st.session_state:
        st.session_state.lerncoach_msgs = []
    quick_prompts = [
        ("🗓️ Wochenplan", "Erstelle mir einen optimalen Wochenplan für die nächsten 7 Tage."),
        ("⏰ Zeitmanagement", "Wie manage ich Lernzeit am besten bei X Stunden/Tag?"),
        ("🔥 Motivationskrise", "Ich bin demotiviert und weiß nicht weiter. Was soll ich jetzt tun?"),
        ("📊 Fehleranalyse", "Analysiere meine häufigsten Klausurfehler und gib Lernempfehlungen."),
    ]
    cols_q = st.columns(4)
    for i,(label,prompt) in enumerate(quick_prompts):
        if cols_q[i].button(label, key=f"lc_btn_{i}", use_container_width=True):
            st.session_state.lerncoach_msgs.append({"role":"user","content":prompt}); st.rerun()
    st.divider()
    for msg in st.session_state.lerncoach_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if st.session_state.lerncoach_msgs and st.session_state.lerncoach_msgs[-1]["role"] == "user":
        with st.chat_message("assistant"):
            resp = st.write_stream(chat_stream(st.session_state.lerncoach_msgs, personas.LERNCOACH))
        st.session_state.lerncoach_msgs.append({"role":"assistant","content":resp}); st.rerun()
    user_in = st.chat_input("Frag den Lerncoach...")
    if user_in:
        st.session_state.lerncoach_msgs.append({"role":"user","content":user_in}); st.rerun()
    if st.session_state.lerncoach_msgs:
        if st.button("🗑️ Chat leeren"):
            st.session_state.lerncoach_msgs = []; st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 4: QUELLEN-LOOKUP
# ════════════════════════════════════════════════════════════════
with TABS[3]:
    st.markdown("### 🔍 Verifizierte Quellen-Recherche")
    with st.expander("📋 Zugelassene Quellen (Whitelist)"):
        cols_wl = st.columns(3)
        for i,d in enumerate(VERIFIED_SOURCES):
            icon = "🏛️" if any(x in d for x in ["bverfg","bundesgerichtshof","bverwg","bag","bfh","curia","echr"]) else "📖"
            cols_wl[i%3].markdown(f"{icon} `{d}`")

    sub_q = st.tabs(["🔗 URL abrufen","§ Paragraph","🔍 Suche"])
    with sub_q[0]:
        url_in = st.text_input("URL", placeholder="https://dejure.org/gesetze/BGB/823.html")
        ki_frage = st.text_input("KI-Frage", placeholder="Was ist klausurrelevant?")
        if st.button("🔍 Abrufen", type="primary", disabled=not url_in.strip()):
            if not is_verified(url_in):
                st.error(f"⚠️ Domain nicht in Whitelist.")
            else:
                with st.spinner("Lade Quelle..."):
                    result = fetch_clean_text(url_in)
                if result:
                    title, text = result
                    st.markdown(f"### 📄 {title}")
                    st.link_button("🔗 Original öffnen", url_in)
                    with st.expander("Volltext"):
                        st.text(text[:4000] + ("..." if len(text)>4000 else ""))
                    frage = ki_frage.strip() or "Fasse das Wesentliche zusammen und erkläre die Examensrelevanz."
                    prompt = f"Quelle: {title}\nURL:{url_in}\n\nInhalt:\n{text[:6000]}\n\nFrage: {frage}"
                    st.markdown("### 🧠 KI-Einordnung")
                    with st.chat_message("assistant"):
                        resp = chat_complete([{"role":"user","content":prompt}], personas.REPETITOR)
                        st.markdown(resp)
                else:
                    st.error("Seite nicht abrufbar.")

    with sub_q[1]:
        cp, cg = st.columns(2)
        with cp: para = st.text_input("Paragraph", placeholder="823")
        with cg: gesetz = st.selectbox("Gesetzbuch", ["BGB","StGB","StPO","ZPO","GG","VwGO","VwVfG","HGB","GmbHG","AktG","InsO"])
        if st.button("§ Nachschlagen", disabled=not para.strip()):
            url = f"https://dejure.org/gesetze/{gesetz}/{para}.html"
            st.link_button(f"🔗 § {para} {gesetz} auf dejure.org", url)
            with st.spinner("Lade Normtext..."):
                result = fetch_clean_text(url, max_chars=4000)
            if result:
                title, text = result
                with st.expander("Normtext"): st.text(text[:2000])
                prompt = (f"Erkläre § {para} {gesetz} examensnah:\n"
                          f"1. Tatbestand · 2. Rechtsfolge · 3. Examensrelevanz · 4. Abgrenzungen\n\n"
                          f"Normtext:\n{text[:2000]}")
                st.markdown("### 🧠 Examenseinordnung")
                with st.chat_message("assistant"):
                    resp = chat_complete([{"role":"user","content":prompt}], personas.REPETITOR)
                    st.markdown(resp)
            else:
                st.link_button("Alternativ: gesetze-im-internet.de",
                               f"https://www.gesetze-im-internet.de/{gesetz.lower()}/_{para}.html")

    with sub_q[2]:
        col_st, col_sq = st.columns([1,3])
        with col_st: suchtyp = st.selectbox("Typ", ["Norm","BGH-Urteil","BVerfG-Entscheidung","BVerwG","Landesrecht"])
        with col_sq: suchbegriff = st.text_input("Suchbegriff", placeholder="§ 823 BGB, BVerfGE 7 198")
        if st.button("🔍 Suchen", disabled=not suchbegriff.strip()):
            vorschlaege = [f"https://dejure.org/suche?q={suchbegriff.replace(' ','+')}"]
            if "BGH" in suchtyp: vorschlaege.append("https://www.bundesgerichtshof.de/")
            elif "BVerfG" in suchtyp: vorschlaege.append("https://www.bverfg.de/")
            elif "Landesrecht" in suchtyp: vorschlaege.append(f"https://recht.nrw.de/lmi/owa/br_suche?suche={suchbegriff.replace(' ','+')}")
            for v in vorschlaege: st.link_button(f"🔗 {v}", v)
            prompt = f"Erkläre examensnah: **{suchbegriff}**\nRechtsgebiet ableiten und strukturiert erklären."
            with st.chat_message("assistant"):
                resp = chat_complete([{"role":"user","content":prompt}], personas.REPETITOR)
                st.markdown(resp)

# ════════════════════════════════════════════════════════════════
# TAB 5: NEWS & RECHTSPRECHUNG
# ════════════════════════════════════════════════════════════════
with TABS[4]:
    st.markdown("### ⚖️ Rechtsprechung & News")
    st.caption("LTO RSS-Feeds · Examensrelevanz-Filter · KI-Einordnung")

    col_feeds, col_filter = st.columns([2, 1])
    with col_feeds:
        selected_feeds = st.multiselect("Kategorien", list(LTO_FEEDS.keys()), default=DEFAULT_FEEDS)
    with col_filter:
        nur_relevant = st.checkbox("Nur examensrelevant", value=True)
        limit = st.slider("Anzahl", 5, 30, 12)

    if not selected_feeds:
        st.info("Bitte mindestens eine Kategorie auswählen.")
    else:
        with st.spinner("Lade News..."):
            items = fetch_all_lto_news(tuple(selected_feeds), limit_per_feed=8)
        if nur_relevant:
            items = [i for i in items if is_exam_relevant(i)]
        items = items[:limit]
        if not items:
            st.info("Keine News gefunden. Filter anpassen.")
        else:
            st.caption(f"{len(items)} Artikel")
            for news_idx, item in enumerate(items):
                pub = item.get("published")
                pub_str = pub.strftime("%d.%m.%Y %H:%M") if pub else "—"
                is_rel = is_exam_relevant(item)
                # Key: news_idx ist garantiert eindeutig (0, 1, 2, ...)
                ki_key = f"news_ki_btn_{news_idx}"

                with st.container(border=True):
                    col_t, col_b = st.columns([4, 1])
                    with col_t:
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"📅 {pub_str} · {item.get('category','?')} · LTO")
                    with col_b:
                        if is_rel:
                            st.success("⚖️ Examen")
                    if item.get("summary"):
                        st.markdown(
                            f'<div style="font-size:.82rem;color:#44403c;line-height:1.5;'
                            f'margin:.2rem 0 .4rem">{item["summary"][:280]}...</div>',
                            unsafe_allow_html=True)
                    col_lnk, col_ki, col_sp = st.columns([1, 1, 3])
                    if item.get("link"):
                        col_lnk.link_button("🔗 Artikel", item["link"])
                    if col_ki.button("🧠 KI", key=ki_key):
                        prompt = (
                            f"Ordne diesen Artikel für das Jurastudium ein:\n"
                            f"Titel: {item['title']}\n"
                            f"Inhalt: {item.get('summary','')}\n\n"
                            f"1. Examensrelevanz + Begründung\n"
                            f"2. Betroffene Normen\n"
                            f"3. Was muss ein Examensstudent wissen?")
                        with st.chat_message("assistant"):
                            resp = chat_complete(
                                [{"role": "user", "content": prompt}],
                                personas.REPETITOR)
                            st.markdown(resp)
