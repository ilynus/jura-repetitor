"""Lernen & Wiederholen — Chat, Karteikarten, Schemata, Streitstände, Normennetz, Anspruchsgrundlagen."""
from __future__ import annotations
import json
import random
import streamlit as st
import streamlit.components.v1 as components

from src import personas, srs
from src.auth import require_login
from src.config import PATH_FLASHCARDS, PATH_MATERIALS, PATH_SHARED_MATERIALS, SOURCE_BADGE, SOURCE_LLM_TAG, SOURCE_TYPE_PERSONAL, SOURCE_TYPE_SHARED, personal_path
from src.github_db import read_json, write_json, now_iso
from src.llm import chat_stream, json_complete, chat_complete
from src.schemas_data import SCHEMAS, get_all_topics, search as schema_search
from src.score import award_xp, show_xp_toast
from src.theme import apply_theme, gold_divider, page_header, section_header, render_top_bar
from src.score import get_level_info, get_score

apply_theme()
user = require_login()
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp",0)
info = get_level_info(xp)
render_top_bar(user["display_name"], xp, info["name"], info["icon"])
page_header("Lernen & Wiederholen", "Chat · Karteikarten · Schemata · Streitstände · Normennetz · Anspruchsgrundlagen", "📚")

TABS = st.tabs(["💬 Chat", "🎴 Karteikarten", "🗂️ Schemata", "⚔️ Streitstände", "🔗 Normennetz", "📊 Anspruchsgrundlagen"])

# ════════════════════════════════════════════════════════════════
# TAB 1: CHAT
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    ROLES = {
        "🎓 Examensbegleiter": personas.EXAMENSBEGLEITER,
        "📖 Repetitor": personas.REPETITOR,
        "🧑‍🏫 AG-Leiter": personas.AG_LEITER,
        "🤝 Lernpartner": personas.LERNPARTNER,
        "📅 Lerncoach": personas.LERNCOACH,
    }
    col_r, col_m = st.columns([1, 2])
    with col_r:
        role = st.selectbox("Rolle", list(ROLES.keys()))
    shared_m = read_json(PATH_SHARED_MATERIALS(), default=[]) or []
    personal_m = read_json(PATH_MATERIALS(), default=[]) or []
    for m in shared_m: m.setdefault("source_type", SOURCE_TYPE_SHARED)
    for m in personal_m: m.setdefault("source_type", SOURCE_TYPE_PERSONAL)
    all_mats = shared_m + personal_m
    with col_m:
        if all_mats:
            def _lbl(m): return f"{SOURCE_BADGE.get(m.get('source_type','personal'),'?')} {m['name']}"
            chosen = st.multiselect("Materialien", [_lbl(m) for m in all_mats], default=[_lbl(m) for m in all_mats])
            active_mats = []
            for m in all_mats:
                if _lbl(m) in chosen:
                    e = dict(m)
                    e["topic"] = f"{SOURCE_LLM_TAG.get(m.get('source_type','personal'),'')} | {m.get('topic','')}"
                    active_mats.append(e)
        else:
            st.info("Keine Materialien — unter 📂 Materialien hochladen.")
            active_mats = []

    if st.session_state.get("chat_role") != role:
        st.session_state.chat_msgs = []
        st.session_state.chat_role = role

    # Quick Commands
    section_header("⚡","Quick-Commands")
    cmd_keys = list(personas.QUICK_COMMANDS.keys())
    for row_start in range(0, len(cmd_keys), 4):
        cols = st.columns(4)
        for i, label in enumerate(cmd_keys[row_start:row_start+4]):
            if cols[i].button(label, key=f"qc_{row_start+i}", use_container_width=True):
                st.session_state.pending_prefix = personas.QUICK_COMMANDS[label]
                st.rerun()

    gold_divider()
    for msg in st.session_state.get("chat_msgs", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prefix = st.session_state.pop("pending_prefix", "")
    if prefix:
        st.info(f"💡 `{prefix[:60].strip()}...`")
    user_in = st.chat_input("Frag den Examensbegleiter...")
    if user_in:
        prompt = (prefix + user_in) if prefix else user_in
        msgs = st.session_state.get("chat_msgs", [])
        msgs.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            resp = st.write_stream(chat_stream(msgs, ROLES[role], active_mats))
        msgs.append({"role":"assistant","content":resp})
        st.session_state.chat_msgs = msgs

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🗑️ Chat leeren"):
            st.session_state.chat_msgs = []
            st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 2: KARTEIKARTEN
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    def _load_cards(): return read_json(PATH_FLASHCARDS(), default=[]) or []
    def _save_cards(c, msg): return write_json(PATH_FLASHCARDS(), c, commit_msg=msg)

    sub_tabs = st.tabs(["📖 Lernen", "✨ Generieren", "📚 Alle Karten"])

    with sub_tabs[0]:
        cards = _load_cards()
        due = [c for c in cards if srs.is_due(c.get("srs", srs.new_card_state()))]
        if not cards:
            st.info("Noch keine Karten. Gehe zu **✨ Generieren**.")
        elif not due:
            st.success(f"🎉 Alle {len(cards)} Karten für heute erledigt!")
        else:
            if st.session_state.get("karten_due_count") != len(due):
                random.shuffle(due)
                st.session_state.karten_due = due
                st.session_state.karten_idx = 0
                st.session_state.karten_show_back = False
                st.session_state.karten_due_count = len(due)
            today_cards = st.session_state.karten_due
            idx = st.session_state.karten_idx
            if idx >= len(today_cards):
                st.success("🎉 Alle fälligen Karten heute geschafft!")
                if st.button("Neu starten"): del st.session_state.karten_idx; st.rerun()
            else:
                card = today_cards[idx]
                st.caption(f"Karte {idx+1}/{len(today_cards)} · {card.get('topic','?')} · Schwierigkeit {card.get('difficulty','?')}")
                st.markdown(f"### 🟦 Frage\n> {card['front']}")
                if not st.session_state.karten_show_back:
                    if st.button("🔎 Lösung zeigen", type="primary", use_container_width=True):
                        st.session_state.karten_show_back = True; st.rerun()
                else:
                    st.markdown(f"### 🟩 Antwort\n{card['back']}")
                    if card.get("source"): st.caption(f"📚 {card['source']}")
                    st.divider()
                    def _grade(g):
                        card["srs"] = srs.update(card.get("srs", srs.new_card_state()), g)
                        all_c = _load_cards()
                        for i,x in enumerate(all_c):
                            if x.get("id") == card.get("id"): all_c[i] = card; break
                        _save_cards(all_c, f"review:{card.get('id')}")
                        xp_map={0:"card_again",3:"card_hard",4:"card_good",5:"card_easy"}
                        e = award_xp(xp_map.get(g,"card_good"), note=card.get("front","")[:40])
                        show_xp_toast(e)
                        st.session_state.karten_idx += 1
                        st.session_state.karten_show_back = False; st.rerun()
                    c1,c2,c3,c4 = st.columns(4)
                    if c1.button("😵 Nochmal", use_container_width=True): _grade(0)
                    if c2.button("😐 Schwer", use_container_width=True): _grade(3)
                    if c3.button("🙂 Gut", use_container_width=True): _grade(4)
                    if c4.button("😎 Einfach", use_container_width=True): _grade(5)

    with sub_tabs[1]:
        gen_src = st.radio("Quelle", ["Aus Material","Aus Thema"], horizontal=True)
        mats_all = (read_json(PATH_SHARED_MATERIALS(), default=[]) or []) + (read_json(PATH_MATERIALS(), default=[]) or [])
        if gen_src == "Aus Material":
            if not mats_all: st.info("Keine Materialien vorhanden.")
            else:
                mat_choice = st.selectbox("Material", [m["name"] for m in mats_all])
                focus = st.text_input("Fokus (optional)", placeholder="Nur §§ 433-453 BGB")
                n = st.slider("Anzahl Karten", 5, 40, 12)
                if st.button("🪄 Karten generieren", type="primary"):
                    mat = next(m for m in mats_all if m["name"] == mat_choice)
                    prompt = f"Erstelle {n} Karteikarten.\n{('Fokus: '+focus) if focus else ''}\n\n# {mat['name']}\n{mat['text'][:8000]}"
                    with st.spinner("Generiere Karten (Haiku)..."):
                        raw = json_complete(prompt, personas.FLASHCARD_GENERATOR)
                    try:
                        data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                        new_cards = data.get("cards", [])
                    except: new_cards = []; st.error("Parse-Fehler"); st.code(raw)
                    if new_cards:
                        existing = _load_cards()
                        next_id = max((c.get("id",0) for c in existing), default=0) + 1
                        for c in new_cards:
                            c["id"] = next_id; c["source_doc"] = mat_choice
                            c["srs"] = srs.new_card_state(); next_id += 1
                        existing.extend(new_cards)
                        _save_cards(existing, f"add {len(new_cards)} cards")
                        e = award_xp("material")
                        st.success(f"✅ {len(new_cards)} Karten hinzugefügt.")
        else:
            thema = st.text_input("Thema", placeholder="§ 280 BGB, Notwehr, Anfechtungsklage")
            n = st.slider("Anzahl", 5, 30, 10, key="n_thema")
            if st.button("🪄 Generieren", type="primary", disabled=not thema.strip()):
                prompt = f"Erstelle {n} Karteikarten zu: {thema}"
                with st.spinner("Generiere (Haiku)..."):
                    raw = json_complete(prompt, personas.FLASHCARD_GENERATOR)
                try:
                    data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                    new_cards = data.get("cards", [])
                except: new_cards = []; st.error("Parse-Fehler")
                if new_cards:
                    existing = _load_cards()
                    next_id = max((c.get("id",0) for c in existing), default=0) + 1
                    for c in new_cards:
                        c["id"] = next_id; c["source_doc"] = thema; c["srs"] = srs.new_card_state(); next_id += 1
                    existing.extend(new_cards)
                    _save_cards(existing, f"add cards: {thema}")
                    st.success(f"✅ {len(new_cards)} Karten erstellt.")

    with sub_tabs[2]:
        cards = _load_cards()
        s = srs.stats(cards)
        c1,c2,c3 = st.columns(3)
        c1.metric("Gesamt",s["total"]); c2.metric("Heute fällig",s["due"]); c3.metric("Gefestigt",s["learned"])
        topics = sorted({c.get("topic","—") for c in cards if c.get("topic")})
        f_topic = st.multiselect("Filter", topics)
        visible = [c for c in cards if not f_topic or c.get("topic") in f_topic]
        for c in visible:
            with st.expander(c["front"]):
                st.markdown(c["back"])
                st.caption(f"ID {c.get('id')} · {c.get('topic','—')} · fällig: {c.get('srs',{}).get('due','?')}")
                if st.button("🗑️", key=f"card_del_{i}"):
                    cards = [x for x in cards if x.get("id") != c.get("id")]
                    _save_cards(cards, f"delete card {c.get('id')}"); st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 3: SCHEMATA
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    sub_s = st.tabs(["📚 Bibliothek","✨ Generieren"])
    with sub_s[0]:
        col_q, col_f = st.columns([2,1])
        with col_q: query = st.text_input("🔍 Suche", placeholder="Anfechtung, Notwehr, Anfechtungsklage")
        with col_f:
            topics_list = ["Alle"] + get_all_topics()
            sel_topic = st.selectbox("Rechtsgebiet", topics_list)
        results = schema_search(query) if query else ([s for s in SCHEMAS if s["topic"]==sel_topic] if sel_topic!="Alle" else SCHEMAS)
        st.caption(f"{len(results)} Schemata")
        for s in results:
            stars = "⭐" * s.get("examensrelevanz",1)
            with st.expander(f"**{s['title']}** · {s['topic']} · {stars}"):
                c_n, c_h = st.columns([1,2])
                with c_n:
                    st.markdown("**Normen:**")
                    for n in s.get("normen",[]): st.markdown(f"`{n}`")
                with c_h:
                    if s.get("hinweise"): st.info(f"💡 {s['hinweise']}")
                st.markdown("**Schema:**")
                for step in s.get("schema",[]):
                    indent = step.count("   ")*8
                    st.markdown(f'<div style="margin-left:{indent}px;font-family:\'IBM Plex Mono\',monospace;font-size:.82rem;padding:.08rem 0">{step.strip()}</div>', unsafe_allow_html=True)
                if s.get("klassiker"):
                    st.markdown("**Klausurklassiker:**")
                    for k in s["klassiker"]: st.markdown(f"- 📌 {k}")
                # XP nur 1x pro Schema pro Session
                xp_key = f"xp_schema_{s.get('id','')}"
                if xp_key not in st.session_state:
                    e = award_xp("schema", note=s["title"])
                    show_xp_toast(e) if e else None
                    st.session_state[xp_key] = True

    with sub_s[1]:
        thema_s = st.text_input("Thema/Norm", placeholder="§ 985 BGB, § 242 StGB")
        tiefe = st.radio("Tiefe", ["Klausurschema","Vertiefungsschema"], horizontal=True)
        if st.button("🧠 Schema generieren", type="primary", disabled=not thema_s.strip()):
            prompt = (f"Erstelle vollständiges Prüfungsschema zu: {thema_s}\n"
                      f"Tiefe: {tiefe}\nMit Normen, Definitionen, Klausurtaktik.")
            with st.chat_message("assistant"):
                st.write_stream(chat_stream([{"role":"user","content":prompt}], personas.REPETITOR))
            award_xp("schema", note=thema_s)

# ════════════════════════════════════════════════════════════════
# TAB 4: STREITSTÄNDE + TRAINER + VISUALISIERUNG
# ════════════════════════════════════════════════════════════════
with TABS[3]:
    sub_st = st.tabs(["⚔️ Neuer Streitstand","🏋️ Trainer","📊 Visualisierung","📂 Archiv"])

    with sub_st[0]:
        col1,col2 = st.columns([3,1])
        with col1: streitfrage = st.text_input("Streitfrage", placeholder="Ist der Besitz ein 'sonstiges Recht' i.S.d. § 823 Abs. 1 BGB?")
        with col2: topic = st.selectbox("Gebiet", ["BGB AT","SchuldR AT","SchuldR BT","SachenR","StrafR AT","StrafR BT","GR","AllgVerwR","VerwProzR","ZPO"])
        if st.button("⚔️ Generieren", type="primary", disabled=not streitfrage.strip()):
            prompt = f"Streitfrage: {streitfrage}\nRechtsgebiet: {topic}"
            with st.spinner("Generiere (Haiku)..."):
                raw = json_complete(prompt, personas.STREITSTAND_GENERATOR, max_tokens=2000)
            try:
                streit = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
            except: streit = None; st.error("Parse-Fehler"); st.code(raw)
            if streit:
                st.markdown(f"## {streit.get('streitfrage', streitfrage)}")
                rel_icon = {"hoch":"🔴","mittel":"🟡","niedrig":"🟢"}.get(streit.get("examensrelevanz","mittel"),"🟡")
                st.caption(f"{streit.get('topic',topic)} · Examensrelevanz: {rel_icon} {streit.get('examensrelevanz','?').upper()}")
                if streit.get("problemaufriss"): st.info(f"**Warum relevant?** {streit['problemaufriss']}")
                st.divider()
                ansichten = streit.get("ansichten",[])
                if ansichten:
                    cols_a = st.columns(len(ansichten))
                    for i,(a,col) in enumerate(zip(ansichten,cols_a)):
                        is_hm = any(x in a.get("bezeichnung","").lower() for x in ["h.m","rspr","herrschend"])
                        bg = "#fffbeb" if is_hm else "white"
                        border = "2px solid #c9a84c" if is_hm else "1px solid #f0ede4"
                        with col:
                            st.markdown(
                                f'<div style="background:{bg};border:{border};border-radius:10px;padding:.85rem 1rem">'
                                f'<div style="font-weight:700;color:#1a2744;margin-bottom:.4rem">{"⭐ " if is_hm else ""}{a.get("bezeichnung","?")}</div>'
                                f'<div style="font-size:.84rem;color:#292524">{a.get("these","")}</div>'
                                f'</div>', unsafe_allow_html=True)
                            if a.get("argumente"):
                                for arg in a["argumente"]: st.markdown(f"- ✓ {arg}")
                            if a.get("vertreter"): st.caption(f"Vertreter: {a['vertreter']}")
                if streit.get("stellungnahme"):
                    st.markdown("### 💡 Stellungnahme")
                    st.markdown(streit["stellungnahme"])
                if streit.get("klausurtaktik"):
                    st.success(f"🎯 **Klausurtaktik:** {streit['klausurtaktik']}")
                # Speichern
                streit["timestamp"] = now_iso()
                PATH_STREITS = lambda: personal_path("streitstaende.json")
                existing_s = read_json(PATH_STREITS(), default=[]) or []
                existing_s.append(streit)
                write_json(PATH_STREITS(), existing_s, commit_msg=f"add streit: {streitfrage[:40]}")
                award_xp("streit", note=streitfrage[:40])
                st.success("✅ Gespeichert.")

    with sub_st[1]:  # STREITSTAND-TRAINER
        st.markdown("### 🏋️ Streitstand-Trainer")
        st.caption("Trainiere das Erkennen und Zuordnen von Ansichten zu Streitfragen.")
        if "trainer_state" not in st.session_state:
            st.session_state.trainer_state = {"score": 0, "total": 0, "current": None}
        ts = st.session_state.trainer_state
        quiz_topics = ["BGB AT","SchuldR AT","StrafR AT","GR"]
        if st.button("🎲 Neue Frage", type="primary"):
            topic_q = random.choice(quiz_topics)
            json_schema = '{"frage":"...","antworten":["...","KORREKT:...","..."]}'
            prompt = (f"Erstelle eine Streitstand-Quiz-Frage zu {topic_q}. "
                      f"Format: 1 Streitfrage + 3 Antworten (eine richtig markiert mit 'KORREKT'). "
                      f"Antwort NUR JSON: {json_schema}")
            with st.spinner("Generiere Frage..."):
                raw = json_complete(prompt, "Du erstellst Jura-Quiz-Fragen. Antworte nur mit JSON.", max_tokens=500)
            try:
                q = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                ts["current"] = q
                ts["answered"] = False
                ts["selected"] = None
            except:
                st.error("Fehler beim Generieren.")
        if ts.get("current") and not ts.get("answered"):
            q = ts["current"]
            st.markdown(f"**{q.get('frage','?')}**")
            antworten = q.get("antworten", [])
            random.shuffle(antworten)
            for a in antworten:
                display = a.replace("KORREKT:","").strip()
                if st.button(display, key=f"quiz_opt_{i}"):
                    ts["answered"] = True
                    ts["total"] += 1
                    if a.startswith("KORREKT"):
                        ts["score"] += 1
                        st.success("✅ Richtig!")
                    else:
                        correct = next((x for x in antworten if x.startswith("KORREKT")),None)
                        st.error(f"❌ Falsch. Richtig: {correct.replace('KORREKT:','').strip() if correct else '?'}")
                    st.rerun()
        elif ts.get("answered"):
            st.info(f"Beantwortet! Score: {ts['score']}/{ts['total']} ({int(ts['score']/ts['total']*100) if ts['total'] else 0}%)")
        st.caption(f"Aktueller Score: {ts['score']}/{ts['total']}")

    with sub_st[2]:  # STREITSTAND-VISUALISIERUNG
        st.markdown("### 📊 Streitstand-Visualisierung")
        PATH_STREITS = lambda: personal_path("streitstaende.json")
        streits = read_json(PATH_STREITS(), default=[]) or []
        if not streits:
            st.info("Noch keine Streitstände gespeichert. Erstelle erst einen unter ⚔️ Neuer Streitstand.")
        else:
            sel = st.selectbox("Streitstand auswählen", [s.get("streitfrage","?") for s in streits])
            s = next((x for x in streits if x.get("streitfrage") == sel), None)
            if s:
                rel_color = {"hoch":"#dc2626","mittel":"#d97706","niedrig":"#16a34a"}.get(s.get("examensrelevanz","mittel"),"#d97706")
                st.markdown(
                    f'<div style="background:white;border:1px solid #f0ede4;border-radius:10px;padding:1rem 1.25rem;margin-bottom:.75rem">'
                    f'<div style="font-family:\'Playfair Display\',serif;font-size:1.05rem;font-weight:600;color:#1a2744;margin-bottom:.3rem">{s.get("streitfrage","")}</div>'
                    f'<div style="font-size:.78rem;color:#57534e">{s.get("topic","")} · '
                    f'<span style="color:{rel_color};font-weight:600">{s.get("examensrelevanz","?").upper()}</span></div>'
                    f'</div>', unsafe_allow_html=True)
                ansichten = s.get("ansichten", [])
                if ansichten:
                    cols_v = st.columns(len(ansichten))
                    colors = ["#dbeafe","#dcfce7","#fef9c3","#fce7f3"]
                    borders = ["#3b82f6","#22c55e","#eab308","#ec4899"]
                    for i,(a,col) in enumerate(zip(ansichten, cols_v)):
                        bg = colors[i % len(colors)]
                        bc = borders[i % len(borders)]
                        is_hm = any(x in a.get("bezeichnung","").lower() for x in ["h.m","rspr","herrschend"])
                        with col:
                            star = "⭐ " if is_hm else ""
                            args_html = "".join(
                                f'<div style="font-size:.75rem;color:#44403c;margin:.1rem 0">✓ {arg}</div>'
                                for arg in a.get("argumente", [])
                            )
                            st.markdown(
                                f'<div style="background:{bg};border:2px solid {bc};border-radius:10px;padding:.85rem;height:100%">'
                                f'<div style="font-weight:700;font-size:.85rem;color:#1a2744;margin-bottom:.35rem">{star}{a.get("bezeichnung","?")}</div>'
                                f'<div style="font-size:.8rem;color:#292524;font-style:italic;margin-bottom:.4rem">{a.get("these","")}</div>'
                                f'{args_html}'
                                f'</div>', unsafe_allow_html=True)
                if s.get("stellungnahme"):
                    st.markdown("---")
                    st.markdown(f"**💡 Stellungnahme:** {s['stellungnahme']}")
                if s.get("klausurtaktik"):
                    st.success(f"🎯 {s['klausurtaktik']}")

    with sub_st[3]:  # ARCHIV
        PATH_STREITS = lambda: personal_path("streitstaende.json")
        streits = read_json(PATH_STREITS(), default=[]) or []
        st.caption(f"{len(streits)} gespeicherte Streitstände")
        for s in reversed(streits):
            rel = {"hoch":"🔴","mittel":"🟡","niedrig":"🟢"}.get(s.get("examensrelevanz","mittel"),"🟡")
            with st.expander(f"{rel} {s.get('streitfrage','?')} · {s.get('topic','')}"):
                for a in s.get("ansichten",[]): st.markdown(f"**{a.get('bezeichnung','')}:** {a.get('these','')}")
                if s.get("stellungnahme"): st.info(s["stellungnahme"])
                if s.get("klausurtaktik"): st.success(f"🎯 {s['klausurtaktik']}")

# ════════════════════════════════════════════════════════════════
# TAB 5: NORMENNETZ (D3.js-Visualisierung)
# ════════════════════════════════════════════════════════════════
with TABS[4]:
    st.markdown("### 🔗 Normennetz")
    st.caption("Interaktive Visualisierung von Normbeziehungen — Klicken zum Expandieren, Ziehen zum Bewegen.")

    normennetz_html = """
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <div id="nn" style="width:100%;height:520px;background:#faf8f3;border-radius:10px;border:1px solid #f0ede4;overflow:hidden;position:relative">
    <div id="nn-tooltip" style="position:absolute;background:#1a2744;color:white;padding:6px 10px;border-radius:6px;font-size:11px;font-family:'IBM Plex Sans',sans-serif;pointer-events:none;display:none;z-index:100"></div>
    </div>
    <script>
    const nodes = [
      {id:"BGB",label:"BGB",group:"gesetz",info:"Bürgerliches Gesetzbuch"},
      {id:"§433",label:"§ 433",group:"norm",info:"Vertragstypische Pflichten beim Kaufvertrag"},
      {id:"§280",label:"§ 280",group:"norm",info:"Schadensersatz wegen Pflichtverletzung"},
      {id:"§823",label:"§ 823",group:"norm",info:"Schadensersatzpflicht (Delikt)"},
      {id:"§985",label:"§ 985",group:"norm",info:"Herausgabeanspruch (Eigentümer-Besitzer)"},
      {id:"§812",label:"§ 812",group:"norm",info:"Herausgabepflicht (Bereicherung)"},
      {id:"§119",label:"§ 119",group:"norm",info:"Anfechtbarkeit wegen Irrtums"},
      {id:"§134",label:"§ 134",group:"norm",info:"Gesetzliches Verbot"},
      {id:"§242",label:"§ 242",group:"norm",info:"Leistung nach Treu und Glauben"},
      {id:"StGB",label:"StGB",group:"gesetz",info:"Strafgesetzbuch"},
      {id:"§242StGB",label:"§ 242 StGB",group:"norm",info:"Diebstahl"},
      {id:"§263",label:"§ 263 StGB",group:"norm",info:"Betrug"},
      {id:"§32",label:"§ 32 StGB",group:"norm",info:"Notwehr"},
      {id:"GG",label:"GG",group:"gesetz",info:"Grundgesetz"},
      {id:"Art14",label:"Art. 14 GG",group:"norm",info:"Eigentum und Erbrecht"},
      {id:"Art2",label:"Art. 2 GG",group:"norm",info:"Freie Entfaltung der Persönlichkeit"},
      {id:"VwGO",label:"VwGO",group:"gesetz",info:"Verwaltungsgerichtsordnung"},
      {id:"§42",label:"§ 42 VwGO",group:"norm",info:"Anfechtungs-/Verpflichtungsklage"},
    ];
    const links = [
      {source:"BGB",target:"§433",type:"enthält"},{source:"BGB",target:"§280",type:"enthält"},
      {source:"BGB",target:"§823",type:"enthält"},{source:"BGB",target:"§985",type:"enthält"},
      {source:"BGB",target:"§812",type:"enthält"},{source:"BGB",target:"§119",type:"enthält"},
      {source:"BGB",target:"§134",type:"enthält"},{source:"BGB",target:"§242",type:"enthält"},
      {source:"§433",target:"§280",type:"→ Pflichtverletzung"},{source:"§280",target:"§823",type:"Konkurrenz"},
      {source:"§985",target:"§812",type:"Subsidiarität"},{source:"§119",target:"§134",type:"Nichtigkeit"},
      {source:"StGB",target:"§242StGB",type:"enthält"},{source:"StGB",target:"§263",type:"enthält"},
      {source:"StGB",target:"§32",type:"enthält"},{source:"§242StGB",target:"§263",type:"Abgrenzung"},
      {source:"GG",target:"Art14",type:"enthält"},{source:"GG",target:"Art2",type:"enthält"},
      {source:"Art14",target:"§985",type:"schützt"},{source:"VwGO",target:"§42",type:"enthält"},
    ];
    const colors = {gesetz:"#1a2744",norm:"#c9a84c"};
    const w=document.getElementById("nn").clientWidth, h=520;
    const svg=d3.select("#nn").append("svg").attr("width",w).attr("height",h);
    const g=svg.append("g");
    svg.call(d3.zoom().scaleExtent([0.3,3]).on("zoom",e=>g.attr("transform",e.transform)));
    const sim=d3.forceSimulation(nodes)
      .force("link",d3.forceLink(links).id(d=>d.id).distance(80))
      .force("charge",d3.forceManyBody().strength(-200))
      .force("center",d3.forceCenter(w/2,h/2))
      .force("collision",d3.forceCollide(35));
    const link=g.append("g").selectAll("line").data(links).join("line")
      .attr("stroke","#c9a84c").attr("stroke-opacity",.4).attr("stroke-width",1.5);
    const node=g.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("r",d=>d.group==="gesetz"?20:14)
      .attr("fill",d=>colors[d.group]||"#78716c")
      .attr("stroke","white").attr("stroke-width",2).style("cursor","pointer")
      .call(d3.drag().on("start",e=>{if(!e.active)sim.alphaTarget(.3).restart();e.subject.fx=e.subject.x;e.subject.fy=e.subject.y;})
        .on("drag",e=>{e.subject.fx=e.x;e.subject.fy=e.y;})
        .on("end",e=>{if(!e.active)sim.alphaTarget(0);e.subject.fx=null;e.subject.fy=null;}))
      .on("mouseover",(e,d)=>{const t=document.getElementById("nn-tooltip");t.style.display="block";t.innerHTML=`<strong>${d.label}</strong><br>${d.info}`;t.style.left=(e.offsetX+10)+"px";t.style.top=(e.offsetY-10)+"px";})
      .on("mouseout",()=>{document.getElementById("nn-tooltip").style.display="none";});
    const label=g.append("g").selectAll("text").data(nodes).join("text")
      .text(d=>d.label).attr("font-size",d=>d.group==="gesetz"?11:9)
      .attr("font-family","IBM Plex Sans, sans-serif").attr("fill","white")
      .attr("text-anchor","middle").attr("dominant-baseline","middle").style("pointer-events","none");
    sim.on("tick",()=>{
      link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
      node.attr("cx",d=>d.x).attr("cy",d=>d.y);
      label.attr("x",d=>d.x).attr("y",d=>d.y);
    });
    </script>
    <div style="padding:.5rem .75rem;font-size:.72rem;color:#78716c;font-family:'IBM Plex Sans',sans-serif">
    🔵 Gesetze &nbsp;·&nbsp; 🟡 Normen &nbsp;·&nbsp; Ziehen=Bewegen · Scrollen=Zoomen · Hover=Info
    </div>"""
    components.html(normennetz_html, height=580, scrolling=False)

# ════════════════════════════════════════════════════════════════
# TAB 6: ANSPRUCHSGRUNDLAGEN-MAPPING
# ════════════════════════════════════════════════════════════════
with TABS[5]:
    st.markdown("### 📊 Anspruchsgrundlagen-Mapping")
    st.caption("Hierarchische Übersicht der wichtigsten Anspruchsgrundlagen. Klicke auf eine Karte für das Schema.")

    ansprueche = {
        "Vertragliche Ansprüche": {
            "color": "#dbeafe", "border": "#3b82f6",
            "items": [
                ("§ 433 Abs. 1 BGB", "Kaufpreiszahlung"),
                ("§ 433 Abs. 2 BGB", "Übergabe und Übereignung"),
                ("§ 535 BGB", "Mietzahlung"),
                ("§ 611 BGB", "Dienstlohnzahlung"),
                ("§ 631 BGB", "Werklohnzahlung"),
            ]
        },
        "Schadensersatz": {
            "color": "#fef9c3", "border": "#eab308",
            "items": [
                ("§ 280 Abs. 1 BGB", "Pflichtverletzung"),
                ("§ 280 I, II, 286 BGB", "Verzugschadensersatz"),
                ("§ 280 I, III, 281 BGB", "Nichterfüllung nach Frist"),
                ("§ 823 Abs. 1 BGB", "Deliktischer SE"),
                ("§ 823 Abs. 2 BGB", "Schutzgesetzverletzung"),
                ("§ 826 BGB", "Sittenwidrige Schädigung"),
            ]
        },
        "Herausgabe / Rückabwicklung": {
            "color": "#dcfce7", "border": "#22c55e",
            "items": [
                ("§ 985 BGB", "Vindikation (Eigentümer-Besitzer)"),
                ("§ 812 Abs. 1 S. 1 Alt. 1 BGB", "Leistungskondiktion"),
                ("§ 812 Abs. 1 S. 1 Alt. 2 BGB", "Eingriffskondiktion"),
                ("§ 346 BGB", "Rücktritt + Rückgewähr"),
            ]
        },
        "Öffentliches Recht": {
            "color": "#fce7f3", "border": "#ec4899",
            "items": [
                ("§ 839 BGB i.V.m. Art. 34 GG", "Amtshaftung"),
                ("Art. 14 GG", "Enteignungsentschädigung"),
                ("§ 113 Abs. 1 S. 2 VwGO", "Folgenbeseitigungsanspruch"),
            ]
        },
    }

    cols_a = st.columns(2)
    for i, (category, data) in enumerate(ansprueche.items()):
        with cols_a[i % 2]:
            items_html = "".join(
                f'<div style="display:flex;justify-content:space-between;padding:.25rem 0;'
                f'border-bottom:1px solid rgba(0,0,0,.06);font-size:.79rem">'
                f'<code style="color:#1a2744;font-family:\'IBM Plex Mono\',monospace;'
                f'font-size:.75rem;background:none">{norm}</code>'
                f'<span style="color:#44403c">{desc}</span></div>'
                for norm, desc in data["items"]
            )
            st.markdown(
                f'<div style="background:{data["color"]};border:1.5px solid {data["border"]};'
                f'border-radius:10px;padding:.85rem 1rem;margin-bottom:.75rem">'
                f'<div style="font-family:\'Playfair Display\',serif;font-weight:600;'
                f'color:#1a2744;margin-bottom:.5rem">{category}</div>'
                f'{items_html}</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("**KI-Anspruchsanalyse** — Sachverhalt eingeben:")
    sach = st.text_area("Sachverhalt", height=100, placeholder="A verkauft B ein Fahrrad für 200€...")
    if st.button("🔍 Ansprüche analysieren", type="primary", disabled=not sach.strip()):
        prompt = (f"Identifiziere alle in Betracht kommenden Anspruchsgrundlagen:\n\n{sach}\n\n"
                  f"Für jede Anspruchsgrundlage: Norm, Anspruchsinhaber, Anspruchsgegner, "
                  f"kurze Prüfung (bejaht/fraglich/verneint), Begründung.")
        with st.chat_message("assistant"):
            st.write_stream(chat_stream([{"role":"user","content":prompt}], personas.REPETITOR))
