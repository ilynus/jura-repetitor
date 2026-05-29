"""Klausur & Prüfung — Korrektor, Fehler-Heatmap, Klausur-Diff, Fall-Generator, Examenssimulation, Mündlich, Aktenvortrag."""
from __future__ import annotations
import json
import difflib
import datetime as dt
import streamlit as st
import streamlit.components.v1 as components

from src import personas
from src.auth import require_login
from src.config import PATH_CORRECTIONS, PATH_MATERIALS, PATH_SHARED_MATERIALS, personal_path
from src.github_db import read_json, write_json, now_iso, list_dir
from src.llm import chat_stream, chat_complete, json_complete, heavy_complete
from src.score import award_xp, get_level_info, get_score, show_xp_toast
from src.theme import apply_theme, gold_divider, page_header, render_top_bar

apply_theme()
user = require_login()
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp",0)
info = get_level_info(xp)
render_top_bar(user["display_name"], xp, info["name"], info["icon"])
page_header("Klausur & Prüfung", "Korrektor · Fehler-Heatmap · Klausur-Diff · Fall-Generator · Examenssimulation · Mündlich · Aktenvortrag", "✍️")

TABS = st.tabs(["✍️ Korrektor","🔥 Fehler-Heatmap","🔍 Klausur-Diff","📋 Fall-Generator","🎓 Examenssimulation","🎤 Mündliche Prüfung","📁 Aktenvortrag"])

# ════════════════════════════════════════════════════════════════
# TAB 1: KORREKTOR
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    with st.form("korrekt_form"):
        col1,col2 = st.columns([2,1])
        with col1: title = st.text_input("Klausurtitel", placeholder="AG-Klausur SchuldR BT")
        with col2:
            art = st.selectbox("Art", ["Examensklausur (5h)","AG-Klausur","Übungsklausur","Hausarbeit"])
            ziel = st.slider("Zielpunktzahl", 4, 18, 10)
        sachverhalt = st.text_area("Sachverhalt (empfohlen)", height=120, placeholder="Original-Sachverhalt...")
        klausur = st.text_area("Deine Lösung", height=380, placeholder="Hier den Klausurtext einfügen...")
        use_mats = st.checkbox("Materialien als Referenz")
        submitted = st.form_submit_button("✍️ Korrigieren (Opus 4.7)", type="primary", use_container_width=True)
    if submitted:
        if not klausur.strip(): st.error("Bitte Klausurtext einfügen.")
        else:
            mats = None
            if use_mats:
                shared = read_json(PATH_SHARED_MATERIALS(), default=[]) or []
                personal = read_json(PATH_MATERIALS(), default=[]) or []
                mats = shared + personal
            msg = (f"# {title or 'Klausur'}\n# Art: {art}\n# Zielpunkte: {ziel}\n"
                   + (f"# Sachverhalt:\n{sachverhalt}\n\n" if sachverhalt.strip() else "")
                   + f"# Lösung:\n{klausur}")
            with st.spinner("Korrigiere mit Opus 4.7 (30-60 Sek.)..."):
                correction = heavy_complete([{"role":"user","content":msg}], personas.KORREKTOR, mats)
            st.divider()
            st.markdown("## 📝 Korrektur")
            st.markdown(correction)
            ts = now_iso()
            record = {"timestamp":ts,"title":title or "Klausur","art":art,"ziel":ziel,
                      "sachverhalt":sachverhalt,"klausur":klausur,"correction":correction}
            write_json(PATH_CORRECTIONS(ts), record, commit_msg=f"correction: {title or ts}")
            earned = award_xp("correction", note=title or "Klausur")
            show_xp_toast(earned, "Klausur korrigiert")
            st.success("✅ Gespeichert.")
            st.download_button("⬇️ Korrektur als Markdown",
                               f"# {title}\n\n{correction}", f"korrektur_{ts}.md", "text/markdown")

# ════════════════════════════════════════════════════════════════
# TAB 2: FEHLER-HEATMAP
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    st.markdown("### 🔥 Fehler-Heatmap")
    st.caption("Zeigt wo in deinen Klausuren Fehler auftreten — nach Rechtsgebiet und Fehlertyp.")

    corrections_path = personal_path("corrections")
    all_corrections = []
    try:
        corr_files = list_dir(corrections_path)
        for f in corr_files[-20:]:  # letzte 20
            c = read_json(f, default=None)
            if c: all_corrections.append(c)
    except Exception:
        pass

    if not all_corrections:
        st.info("Noch keine Korrekturen vorhanden. Korrigiere zuerst eine Klausur unter **✍️ Korrektor**.")
    else:
        # Analysiere Fehlertypen via KI
        if st.button("🤖 Fehler analysieren", type="primary"):
            summaries = "\n\n---\n\n".join([
                f"Klausur: {c.get('title','?')}\nKorrektur:\n{c.get('correction','')[:800]}"
                for c in all_corrections[-10:]
            ])
            prompt = (f"Analysiere folgende Klausur-Korrekturen und extrahiere Fehlermuster.\n\n{summaries}\n\n"
                      f"Erstelle eine JSON-Tabelle der häufigsten Fehler:\n"
                      f"{{\"fehler\":[{{\"typ\":\"Aufbaufehler|Subsumtion|Normfehler|Streitstand|Sprache|Schwerpunkt\","
                      f"\"rechtsgebiet\":\"BGB AT|SchuldR|...\",\"anzahl\":2,\"beispiel\":\"...\"}}]}}")
            with st.spinner("Analysiere Fehlertypen..."):
                raw = json_complete(prompt, "Analysiere juristische Klausurfehler. Antworte nur mit JSON.", max_tokens=1500)
            try:
                data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                fehler_list = data.get("fehler", [])
            except:
                fehler_list = []
                st.error("Analyse fehlgeschlagen.")
                st.code(raw)

            if fehler_list:
                st.session_state.fehler_heatmap = fehler_list
                st.rerun()

        if "fehler_heatmap" in st.session_state:
            fehler_list = st.session_state.fehler_heatmap
            typen = sorted(set(f["typ"] for f in fehler_list))
            gebiete = sorted(set(f["rechtsgebiet"] for f in fehler_list))
            fehler_map = {(f["typ"], f["rechtsgebiet"]): f["anzahl"] for f in fehler_list}
            max_val = max(fehler_map.values(), default=1)

            def heat_color(val, max_v):
                if val == 0: return "#f0ede4"
                ratio = val / max_v
                r = int(220 + (220 - 26) * (1 - ratio))
                g = int(38 + 38 * (1 - ratio))
                b = int(38 + 38 * (1 - ratio))
                return f"rgb({int(220*ratio+240*(1-ratio))},{int(220*(1-ratio)+38*ratio)},{int(220*(1-ratio)+38*ratio)})"

            st.markdown("**Fehler-Heatmap** (Rot = häufig, Grau = selten)")
            # Header
            header = '<div style="display:grid;grid-template-columns:140px ' + ' '.join(['80px']*len(typen)) + ';gap:2px;margin-bottom:4px">'
            header += '<div></div>'
            for t in typen:
                header += f'<div style="font-size:.68rem;font-weight:700;color:#1a2744;text-align:center;writing-mode:vertical-lr;transform:rotate(180deg);height:80px;line-height:1.2">{t}</div>'
            header += '</div>'
            st.markdown(header, unsafe_allow_html=True)
            for gebiet in gebiete:
                row = f'<div style="display:grid;grid-template-columns:140px ' + ' '.join(['80px']*len(typen)) + ';gap:2px;margin-bottom:2px">'
                row += f'<div style="font-size:.75rem;color:#44403c;display:flex;align-items:center;padding-right:8px">{gebiet}</div>'
                for t in typen:
                    val = fehler_map.get((t, gebiet), 0)
                    color = heat_color(val, max_val)
                    row += f'<div style="background:{color};border-radius:4px;height:36px;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:600;color:{"white" if val > max_val*0.5 else "#292524"}">{val if val > 0 else ""}</div>'
                row += '</div>'
                st.markdown(row, unsafe_allow_html=True)
            st.divider()
            st.markdown("**Häufigste Fehler im Detail:**")
            for f in sorted(fehler_list, key=lambda x: x["anzahl"], reverse=True)[:5]:
                st.markdown(
                    f'<div style="background:white;border:1px solid #f0ede4;border-radius:8px;padding:.6rem .85rem;margin-bottom:.35rem">'
                    f'<span style="font-weight:600;color:#1a2744">{f["typ"]}</span> · {f["rechtsgebiet"]} · '
                    f'<span style="color:#dc2626;font-weight:600">{f["anzahl"]}×</span>'
                    f'<div style="font-size:.78rem;color:#57534e;margin-top:.2rem">{f.get("beispiel","")}</div>'
                    f'</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 3: KLAUSUR-DIFF
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    st.markdown("### 🔍 Klausur-Diff")
    st.caption("Vergleiche zwei Versionen deiner Klausurlösung oder deine Lösung mit einer Musterlösung.")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        v1_label = st.text_input("Bezeichnung Version 1", value="Meine Lösung")
        v1 = st.text_area("Text Version 1", height=300, placeholder="Erste Version hier einfügen...", key="diff_v1")
    with col_d2:
        v2_label = st.text_input("Bezeichnung Version 2", value="Musterlösung")
        v2 = st.text_area("Text Version 2", height=300, placeholder="Zweite Version hier einfügen...", key="diff_v2")
    if st.button("🔍 Vergleichen", type="primary") and v1.strip() and v2.strip():
        d = difflib.HtmlDiff(wrapcolumn=80)
        diff_html = d.make_table(
            v1.splitlines(), v2.splitlines(),
            fromdesc=v1_label, todesc=v2_label,
            context=True, numlines=3
        )
        styled_diff = f"""
        <style>
        .diff table{{width:100%;font-family:'IBM Plex Sans',sans-serif;font-size:.8rem;border-collapse:collapse}}
        .diff td{{padding:3px 8px;border:1px solid #f0ede4;vertical-align:top}}
        .diff .diff_header{{background:#1a2744;color:#e8c97b;font-weight:600;padding:4px 8px}}
        .diff .diff_next{{background:#f0ede4}}
        .diff_add{{background:#dcfce7!important}}
        .diff_chg{{background:#fef9c3!important}}
        .diff_sub{{background:#fee2e2!important}}
        </style>
        <div class="diff" style="overflow-x:auto">{diff_html}</div>"""
        components.html(styled_diff, height=500, scrolling=True)
        st.divider()
        if st.button("🤖 KI-Analyse der Unterschiede"):
            prompt = (f"Vergleiche folgende zwei Klausurlösungen und erkläre die wesentlichen Unterschiede:\n\n"
                      f"## {v1_label}:\n{v1[:2000]}\n\n## {v2_label}:\n{v2[:2000]}\n\n"
                      f"Was fehlt in Version 1? Was ist in Version 2 besser? Welche Verbesserungen sind examensrelevant?")
            with st.chat_message("assistant"):
                st.write_stream(chat_stream([{"role":"user","content":prompt}], personas.KORREKTOR))

# ════════════════════════════════════════════════════════════════
# TAB 4: FALL-GENERATOR
# ════════════════════════════════════════════════════════════════
with TABS[3]:
    sub_f = st.tabs(["✨ Generieren","📂 Archiv"])
    with sub_f[0]:
        col1,col2,col3 = st.columns(3)
        with col1:
            rechtsgebiet = st.selectbox("Rechtsgebiet", [
                "BGB AT","Schuldrecht AT","Schuldrecht BT","Sachenrecht",
                "Strafrecht AT","Strafrecht BT","Öffentliches Recht","Verwaltungsrecht",
                "Polizeirecht","Verfassungsrecht","Europarecht","ZPO"])
        with col2: schwierigkeit = st.select_slider("Schwierigkeit", ["leicht","mittel","schwer"], "mittel")
        with col3: dauer = st.selectbox("Dauer", ["30 Min","1 Stunde","2 Stunden","5 Stunden (Examen)"])
        dauer_min = {"30 Min":30,"1 Stunde":60,"2 Stunden":120,"5 Stunden (Examen)":300}[dauer]
        thema_hint = st.text_input("Schwerpunkt (optional)", placeholder="§ 280 BGB, Notwehr, Anscheinsvollmacht")
        nrw_focus = st.checkbox("Landesrecht einbeziehen (je nach Profil)", value=True)
        mit_loesung = st.checkbox("Lösungsskizze anzeigen", value=True)
        if st.button("⚡ Fall generieren", type="primary", use_container_width=True):
            prompt = (f"Rechtsgebiet:{rechtsgebiet}\nSchwierigkeit:{schwierigkeit}\n"
                      f"Dauer:{dauer_min} Min\n{'Landesrecht berücksichtigen.\n' if nrw_focus else ''}"
                      + (f"Schwerpunkt:{thema_hint}\n" if thema_hint else "")
                      + f"Lösungsskizze:{'Ja' if mit_loesung else 'Nein'}")
            with st.spinner("Generiere Fall (Haiku)..."):
                raw = json_complete(prompt, personas.CASE_GENERATOR, max_tokens=3000)
            try:
                fall = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
            except: fall = None; st.error("Parse-Fehler"); st.code(raw)
            if fall:
                st.markdown(f"## {fall.get('title','Fall')}")
                c1,c2,c3 = st.columns(3)
                c1.metric("Rechtsgebiet", fall.get("topic",rechtsgebiet))
                c2.metric("Schwierigkeit", fall.get("difficulty",schwierigkeit))
                c3.metric("Dauer", f"{fall.get('duration_min',dauer_min)} Min")
                st.markdown("### 📄 Sachverhalt")
                st.markdown(fall.get("sachverhalt",""))
                st.markdown(f"**Fragestellung:** {fall.get('fragestellung','')}")
                if fall.get("schwerpunkte"):
                    st.markdown("**Schwerpunkte:** " + " · ".join(fall["schwerpunkte"]))
                if mit_loesung and fall.get("loesungsskizze"):
                    with st.expander("📝 Lösungsskizze"):
                        st.markdown(fall["loesungsskizze"])
                if fall.get("erwartungshorizont"):
                    with st.expander("📊 Erwartungshorizont"):
                        eh = fall["erwartungshorizont"]
                        if eh.get("muss"):
                            st.markdown("**Muss:**"); [st.markdown(f"- ✅ {p}") for p in eh["muss"]]
                        if eh.get("soll"):
                            st.markdown("**Soll:**"); [st.markdown(f"- 🎯 {p}") for p in eh["soll"]]
                        if eh.get("kann"):
                            st.markdown("**Kann:**"); [st.markdown(f"- 💡 {p}") for p in eh["kann"]]
                ts = now_iso(); fall["timestamp"] = ts
                PATH_CASES = lambda: personal_path("cases.json")
                existing = read_json(PATH_CASES(), default=[]) or []
                existing.append(fall)
                write_json(PATH_CASES(), existing, commit_msg=f"add case: {fall.get('title',ts)}")
                award_xp("case", note=fall.get("title",""))
                st.success("✅ Fall gespeichert.")
    with sub_f[1]:
        PATH_CASES = lambda: personal_path("cases.json")
        cases = read_json(PATH_CASES(), default=[]) or []
        if not cases: st.info("Noch keine Fälle.")
        else:
            for c in reversed(cases):
                with st.expander(f"📋 {c.get('title','Fall')} · {c.get('topic','')} · {c.get('difficulty','')}"):
                    st.markdown(f"**Sachverhalt:**\n{c.get('sachverhalt','')}")
                    st.markdown(f"**Fragestellung:** {c.get('fragestellung','')}")

# ════════════════════════════════════════════════════════════════
# TAB 5: EXAMENSSIMULATION
# ════════════════════════════════════════════════════════════════
with TABS[4]:
    st.markdown("### 🎓 Examenssimulation")
    st.caption("Simuliert eine vollständige Examensklausur mit Zeitdruck und automatischer Bewertung.")
    if "exam_sim" not in st.session_state:
        st.session_state.exam_sim = {"phase": "config"}
    sim = st.session_state.exam_sim
    if sim["phase"] == "config":
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            exam_subject = st.selectbox("Rechtsgebiet", ["Zivilrecht","Strafrecht","Öffentliches Recht","Gemischt"])
            exam_level = st.selectbox("Niveau", ["Übungsklausur (2h)","AG-Klausur (2h)","Examensklausur (5h)"])
        with col_e2:
            exam_duration = {"Übungsklausur (2h)":120,"AG-Klausur (2h)":120,"Examensklausur (5h)":300}[exam_level]
            st.metric("Bearbeitungszeit", f"{exam_duration} Minuten")
            st.caption("Der Timer läuft sobald du auf Start klickst.")
        if st.button("🎓 Simulation starten", type="primary", use_container_width=True):
            with st.spinner("Generiere Examensfall..."):
                raw = json_complete(
                    f"Rechtsgebiet:{exam_subject}\nSchwierigkeit:schwer\nDauer:{exam_duration} Min\nLösungsskizze:Nein",
                    personas.CASE_GENERATOR, max_tokens=2000
                )
            try:
                fall = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
            except: fall = {"title":"Examensfall","sachverhalt":raw,"fragestellung":"Wie ist die Rechtslage?"}
            sim.update({
                "phase":"running","fall":fall,"duration":exam_duration,
                "start":dt.datetime.now().isoformat(),"answer":""
            })
            st.rerun()
    elif sim["phase"] == "running":
        fall = sim["fall"]
        start = dt.datetime.fromisoformat(sim["start"])
        elapsed = (dt.datetime.now() - start).seconds // 60
        remaining = sim["duration"] - elapsed
        col_timer, col_info = st.columns([1, 3])
        with col_timer:
            color = "#dc2626" if remaining < 30 else "#d97706" if remaining < 60 else "#1a2744"
            st.markdown(
                f'<div class="focus-timer" style="font-size:2rem;color:{color}">'
                f'⏱️ {remaining} Min</div>', unsafe_allow_html=True)
        with col_info:
            st.markdown(f"**{fall.get('title','Examensfall')}** · {fall.get('topic','')} · {fall.get('difficulty','')}")
        st.markdown("---")
        st.markdown("### 📄 Sachverhalt")
        st.markdown(fall.get("sachverhalt",""))
        st.markdown(f"**Aufgabe:** {fall.get('fragestellung','Wie ist die Rechtslage?')}")
        st.markdown("---")
        answer = st.text_area("✍️ Deine Lösung", height=400, key="exam_answer",
                              placeholder="Schreibe hier deine Klausurlösung...")
        col_sub, col_abort = st.columns(2)
        with col_sub:
            if st.button("📤 Abgeben & Korrigieren", type="primary", use_container_width=True):
                sim["answer"] = answer; sim["phase"] = "correction"; st.rerun()
        with col_abort:
            if st.button("❌ Abbrechen", use_container_width=True):
                sim["phase"] = "config"; st.rerun()
        if remaining <= 0:
            st.warning("⏰ Zeit abgelaufen!")
    elif sim["phase"] == "correction":
        fall = sim["fall"]
        answer = sim.get("answer","")
        with st.spinner("Korrigiere Examenslösung mit Opus 4.7..."):
            msg = (f"# Examenssimulation\n# Fall: {fall.get('title','?')}\n"
                   f"# Sachverhalt:\n{fall.get('sachverhalt','')}\n\n"
                   f"# Deine Lösung:\n{answer}")
            correction = heavy_complete([{"role":"user","content":msg}], personas.KORREKTOR)
        st.markdown("## 📝 Korrekturgutachten")
        st.markdown(correction)
        ts = now_iso()
        write_json(PATH_CORRECTIONS(ts), {"timestamp":ts,"title":f"Examen:{fall.get('title','?')}",
            "art":"Examenssimulation","klausur":answer,"correction":correction}, commit_msg=f"exam sim: {ts}")
        award_xp("correction", note="Examenssimulation")
        st.download_button("⬇️ Gutachten", correction, f"examen_{ts}.md", "text/markdown")
        if st.button("🔄 Neue Simulation"): sim["phase"] = "config"; st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 6: MÜNDLICHE PRÜFUNG
# ════════════════════════════════════════════════════════════════
with TABS[5]:
    col1,col2,col3 = st.columns(3)
    with col1: rechtsgebiet_m = st.selectbox("Einstiegsgebiet",["Zivilrecht","Strafrecht","Öffentliches Recht","Gemischt"])
    with col2: stil_m = st.selectbox("Prüfungsstil",["Standard","Wohlwollend","Anspruchsvoll","Sehr streng"])
    with col3: thema_m = st.text_input("Schwerpunkt (optional)", placeholder="Stellvertretung, § 242 StGB")
    if "muendl_msgs" not in st.session_state: st.session_state.muendl_msgs = []
    if "muendl_started" not in st.session_state: st.session_state.muendl_started = False
    col_s, col_r = st.columns([3,1])
    with col_s:
        if not st.session_state.muendl_started:
            if st.button("🎤 Prüfung starten", type="primary", use_container_width=True):
                st.session_state.muendl_started = True
                st.session_state.muendl_msgs = [{"role":"user","content":
                    f"Starte mündliche Prüfung. Gebiet:{rechtsgebiet_m}, Stil:{stil_m}"
                    + (f", Schwerpunkt:{thema_m}" if thema_m else "") + ". Beginne sofort mit deiner ersten Frage."}]
                st.rerun()
    with col_r:
        if st.session_state.muendl_started:
            if st.button("🏁 Beenden", use_container_width=True):
                award_xp("oral_exam", note=rechtsgebiet_m)
                st.session_state.muendl_started = False
                st.session_state.muendl_msgs = []; st.rerun()
    def _build_muendl(stil):
        base = personas.MUENDLICHE_PRUEFUNG
        modifiers = {"Wohlwollend":"\nZusatz: Nach 2 Nachfragen deutlichen Hinweis geben.",
                     "Anspruchsvoll":"\nZusatz: Fordernde Transferfragen, aktuelle Urteile.",
                     "Sehr streng":"\nZusatz: Mehrfach nachfragen, präzise Normnennungen erwarten."}
        return base + modifiers.get(stil,"")
    for msg in st.session_state.muendl_msgs:
        if any(x in msg.get("content","") for x in ["Starte mündliche","starte mündliche"]): continue
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if st.session_state.muendl_started and st.session_state.muendl_msgs:
        last = st.session_state.muendl_msgs[-1]
        if last["role"] == "user":
            with st.chat_message("assistant"):
                resp = st.write_stream(chat_stream(st.session_state.muendl_msgs, _build_muendl(stil_m)))
            st.session_state.muendl_msgs.append({"role":"assistant","content":resp}); st.rerun()
    if st.session_state.muendl_started:
        antwort = st.chat_input("Deine Antwort...")
        if antwort:
            st.session_state.muendl_msgs.append({"role":"user","content":antwort}); st.rerun()
        c1,c2,c3 = st.columns(3)
        if c1.button("📊 Leistungseinschätzung"):
            st.session_state.muendl_msgs.append({"role":"user","content":"Gib mir eine ehrliche Leistungseinschätzung."}); st.rerun()
        if c2.button("➡️ Nächstes Gebiet"):
            st.session_state.muendl_msgs.append({"role":"user","content":"Wechsle zum nächsten Rechtsgebiet."}); st.rerun()
        if c3.button("💡 Hinweis"):
            st.session_state.muendl_msgs.append({"role":"user","content":"Ich stecke fest, bitte gib mir einen Hinweis."}); st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 7: AKTENVORTRAG
# ════════════════════════════════════════════════════════════════
with TABS[6]:
    st.markdown("### 📁 Aktenvortrag-Trainer")
    modus_a = st.radio("Modus", ["🗂️ Gliederungscoach","🎤 Vortragsbewertung","❓ Rückfragen-Simulator"], horizontal=True)
    if "Gliederungscoach" in modus_a:
        aktentyp = st.selectbox("Aktentyp",["Zivilsache","Strafsache","Verwaltungssache"])
        aktentext = st.text_area("Aktenauszug", height=250, placeholder="Akteninhalt hier einfügen...")
        if st.button("🗂️ Gliederung erarbeiten", type="primary", disabled=not aktentext.strip()):
            prompt = f"Aktenvortrag-Gliederung für {aktentyp}:\n{aktentext}\n\nStrukturiere: Sachverhalt→Rechtsfragen→Aufbau→Votum→Kritische Punkte."
            with st.chat_message("assistant"):
                st.write_stream(chat_stream([{"role":"user","content":prompt}], personas.AKTENVORTRAG))
            award_xp("oral_exam", note="Aktenvortrag Gliederung")
    elif "Vortragsbewertung" in modus_a:
        vortrag = st.text_area("Dein Vortrag (als Text)", height=200, placeholder="Vortrag eintippen...")
        kontext = st.text_input("Aktenkontext (optional)")
        if st.button("🎤 Bewerten", type="primary", disabled=not vortrag.strip()):
            prompt = f"Bewerte Aktenvortrag für 2. Examen.\n{('Kontext:'+kontext+chr(10)) if kontext else ''}Vortrag:\n{vortrag}"
            with st.chat_message("assistant"):
                st.write_stream(chat_stream([{"role":"user","content":prompt}], personas.AKTENVORTRAG))
            award_xp("oral_exam", note="Aktenvortrag Bewertung")
    else:
        vortrag_rq = st.text_area("Dein Vortrag/Votum", height=150, placeholder="Kurze Zusammenfassung...")
        if "aktenv_msgs" not in st.session_state: st.session_state.aktenv_msgs = []
        if st.button("❓ Rückfragen starten", type="primary", disabled=not vortrag_rq.strip()):
            st.session_state.aktenv_msgs = [{"role":"user","content":f"Ich habe vorgetragen:\n{vortrag_rq}\nStelle realistische Rückfragen, eine nach der anderen."}]; st.rerun()
        for msg in st.session_state.aktenv_msgs:
            if "habe vorgetragen" in msg.get("content",""): continue
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if st.session_state.aktenv_msgs:
            last = st.session_state.aktenv_msgs[-1]
            if last["role"] == "user":
                with st.chat_message("assistant"):
                    resp = st.write_stream(chat_stream(st.session_state.aktenv_msgs, personas.AKTENVORTRAG))
                st.session_state.aktenv_msgs.append({"role":"assistant","content":resp}); st.rerun()
            antwort_rq = st.chat_input("Deine Antwort auf die Rückfrage...")
            if antwort_rq:
                st.session_state.aktenv_msgs.append({"role":"user","content":antwort_rq}); st.rerun()
