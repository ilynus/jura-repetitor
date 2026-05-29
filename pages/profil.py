"""Profil & Einstellungen — Profil, Persönlicher Assistent, To-do, Feedback, Admin."""
from __future__ import annotations
import datetime as dt
import uuid
import streamlit as st

from src import personas
from src.auth import is_admin, is_logged_in, list_users, promote_to_admin, require_login
from src.bug_reporter import save_bug_report
from src.config import PATH_FEEDBACK, personal_path
from src.github_db import read_json, write_json, now_iso
from src.llm import chat_stream, chat_complete
from src.profile import build_profile_context, get_profile, render_profile_editor, RECHTSGEBIETE
from src.score import ACHIEVEMENTS, get_level_info, get_score, render_achievements_grid
from src.theme import apply_theme, gold_divider, page_header, render_top_bar

apply_theme()
user = require_login()
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp", 0)
info = get_level_info(xp)
render_top_bar(user["display_name"], xp, info["name"], info["icon"])
page_header("Profil & Einstellungen", "Profil · Persönlicher Assistent · Feedback · Admin", "⚙️")

tabs_list = ["👤 Profil", "🤖 Persönlicher Assistent", "🐛 Feedback & Bugs"]
if is_admin():
    tabs_list.append("🛡️ Admin")
TABS = st.tabs(tabs_list)

# ════════════════════════════════════════════════════════════════
# TAB 1: PROFIL
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    profile = get_profile(uname)

    # Profil-Übersicht Banner
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:12px;
        padding:1.25rem 1.5rem;margin-bottom:1rem;border:1px solid rgba(201,168,76,.2)">
        <div style="display:flex;align-items:center;gap:.85rem;flex-wrap:wrap">
          <div style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;color:white">
            {'🛡️' if user['role']=='admin' else '👤'} {user['display_name']}</div>
          <span style="background:rgba(201,168,76,.2);color:#e8c97b;font-size:.75rem;
            font-weight:600;padding:.2rem .65rem;border-radius:99px;border:1px solid rgba(201,168,76,.3)">
            @{user['username']}</span>
          <span style="background:rgba(255,255,255,.1);color:rgba(255,255,255,.75);
            font-size:.75rem;padding:.2rem .65rem;border-radius:99px">
            {info['icon']} Lv.{info['level']} · {info['name']}</span>
        </div>
        <div style="margin-top:.5rem;display:flex;gap:1.25rem;flex-wrap:wrap">
          <span style="color:rgba(255,255,255,.6);font-size:.8rem">
            🏛️ {profile.get('universitaet','—')}</span>
          <span style="color:rgba(255,255,255,.6);font-size:.8rem">
            📚 {profile.get('fachsemester','—')}</span>
          <span style="color:rgba(255,255,255,.6);font-size:.8rem">
            🎯 Ziel: {profile.get('ziel_punkte','—')} Punkte</span>
          {f'<span style="color:rgba(201,168,76,.8);font-size:.78rem">⏰ Examen: {profile["examenstermin"]}</span>' if profile.get("examenstermin") else ''}
        </div></div>""",
        unsafe_allow_html=True,
    )

    col_stats, col_ach = st.columns(2)
    with col_stats:
        st.markdown("#### 📊 Lernstatistik")
        stats = score_data.get("stats", {})
        st.markdown(
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:.5rem">'
            + "".join([
                f'<div style="background:white;border:1px solid #f0ede4;border-radius:8px;padding:.6rem .85rem">'
                f'<div style="font-size:.67rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#57534e">{lbl}</div>'
                f'<div style="font-family:\'Playfair Display\',serif;font-size:1.4rem;font-weight:700;color:#1a2744">{val}</div></div>'
                for lbl,val in [
                    ("Karten gelernt", stats.get("cards_reviewed",0)),
                    ("Klausuren", stats.get("corrections",0)),
                    ("XP gesamt", f"{xp:,}"),
                    ("Login-Streak", f"{score_data.get('streak',0)} Tage"),
                ]
            ]) + '</div>',
            unsafe_allow_html=True,
        )
        if profile.get("schwache_rechtsgebiete"):
            st.markdown("**⚠️ Fokus-Rechtsgebiete:**")
            for r in profile["schwache_rechtsgebiete"]:
                st.markdown(f'<span style="background:#fef9c3;color:#92400e;padding:.18rem .5rem;border-radius:6px;font-size:.8rem;margin:.1rem;display:inline-block">⚠️ {r}</span>', unsafe_allow_html=True)

    with col_ach:
        st.markdown("#### 🏆 Achievements")
        unlocked = set(score_data.get("unlocked_achievements",[]))
        total = len(ACHIEVEMENTS); done = len(unlocked)
        st.progress(done/total if total else 0, text=f"{done}/{total} freigeschaltet")
        recent = [a for a in ACHIEVEMENTS if a["id"] in unlocked][-5:]
        for a in reversed(recent):
            st.markdown(
                f'<div style="background:#fefce8;border:1px solid rgba(201,168,76,.3);border-radius:8px;'
                f'padding:.45rem .75rem;margin-bottom:.25rem;display:flex;align-items:center;gap:.5rem">'
                f'<span style="font-size:1.2rem">{a["icon"]}</span>'
                f'<div><div style="font-weight:600;font-size:.82rem;color:#1a2744">{a["name"]}</div>'
                f'<div style="font-size:.72rem;color:#57534e">{a["desc"]}</div></div>'
                f'<span style="margin-left:auto;font-family:\'IBM Plex Mono\',monospace;'
                f'font-size:.7rem;color:#c9a84c">+{a["xp"]} XP</span></div>',
                unsafe_allow_html=True)

    gold_divider()
    st.markdown("#### ✏️ Profil bearbeiten")
    render_profile_editor(uname)

    with st.expander("👁️ Profil-Vorschau (was Claude sieht)"):
        ctx = build_profile_context(uname)
        st.code(ctx, language="markdown")

# ════════════════════════════════════════════════════════════════
# TAB 2: PERSÖNLICHER ASSISTENT
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    st.markdown("### 🤖 Persönlicher Assistent")
    st.caption("Kennt dein Profil, deinen Fortschritt und deine Schwächen. Ist immer auf deiner Seite.")

    profile = get_profile(uname)
    stats = score_data.get("stats",{})
    weak = profile.get("schwache_rechtsgebiete",[])

    # Kontext-Banner
    st.markdown(
        f'<div style="background:white;border:1px solid #f0ede4;border-radius:10px;'
        f'padding:.75rem 1rem;margin-bottom:.75rem;font-size:.8rem;color:#292524">'
        f'ℹ️ Ich kenne: <strong>{user["display_name"]}</strong> · '
        f'{profile.get("fachsemester","?")} · '
        f'{profile.get("examenstyp","Staatsexamen")} · '
        f'Schwächen: {", ".join(weak[:3]) if weak else "—"} · '
        f'{info["icon"]} Lv.{info["level"]} · {stats.get("corrections",0)} Korrekturen</div>',
        unsafe_allow_html=True,
    )

    # Assistent-System-Prompt mit vollem Kontext
    def _asst_system():
        stat_ctx = (
            f"\n\n# AKTUELLER LERNSTAND\n"
            f"XP: {xp} (Level {info['level']} · {info['name']})\n"
            f"Login-Streak: {score_data.get('streak',0)} Tage\n"
            f"Karteikarten gelernt: {stats.get('cards_reviewed',0)}\n"
            f"Klausuren korrigiert: {stats.get('corrections',0)}\n"
            f"Unlocked Achievements: {len(score_data.get('unlocked_achievements',[]))}/{len(ACHIEVEMENTS)}\n"
        )
        return personas.PERSOENLICHER_ASSISTENT + stat_ctx

    quick_asst = [
        ("🎯 Wo stehe ich?", "Analysiere meinen aktuellen Lernstand ehrlich und sage mir, wo ich im Vergleich zum Examen stehe."),
        ("📊 Was jetzt tun?", "Was soll ich jetzt konkret tun — heute, diese Woche, diesen Monat?"),
        ("💪 Motivation", "Ich bin gerade demotiviert. Hilf mir, wieder anzufangen."),
        ("🧠 Quiz mich", "Stelle mir 3 examensrelevante Fragen zu meinen schwachen Rechtsgebieten."),
    ]
    cols_asst = st.columns(4)
    for i,(label,prompt) in enumerate(quick_asst):
        if cols_asst[i].button(label, key=f"asst_q_{i}", use_container_width=True):
            if "asst_msgs" not in st.session_state: st.session_state.asst_msgs = []
            st.session_state.asst_msgs.append({"role":"user","content":prompt}); st.rerun()

    if "asst_msgs" not in st.session_state:
        st.session_state.asst_msgs = []
    for msg in st.session_state.asst_msgs:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if st.session_state.asst_msgs and st.session_state.asst_msgs[-1]["role"] == "user":
        with st.chat_message("assistant"):
            resp = st.write_stream(chat_stream(st.session_state.asst_msgs, _asst_system()))
        st.session_state.asst_msgs.append({"role":"assistant","content":resp}); st.rerun()
    user_in = st.chat_input("Schreib deinem Assistenten...")
    if user_in:
        st.session_state.asst_msgs.append({"role":"user","content":user_in}); st.rerun()
    if st.session_state.asst_msgs:
        if st.button("🗑️ Chat leeren"): st.session_state.asst_msgs = []; st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 3: FEEDBACK & BUGS
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    st.markdown("### 🐛 Feedback & Verbesserungsvorschläge")
    st.caption("Dein Feedback wird im GitHub-Daten-Repo gespeichert und vom Admin eingesehen.")

    # Eigene Einreichungen
    all_feedback = read_json(PATH_FEEDBACK(), default=[]) or []
    my_feedback = [f for f in all_feedback if f.get("user") == uname]

    with st.form("feedback_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fb_typ = st.selectbox("Kategorie", ["🐛 Bug","✨ Verbesserung","💡 Feature-Wunsch","❓ Frage","👍 Lob"])
            fb_prio = st.select_slider("Wichtigkeit", ["niedrig","mittel","hoch"])
        with col_f2:
            fb_titel = st.text_input("Titel *", placeholder="Kurze Beschreibung")
        fb_beschr = st.text_area("Beschreibung", height=120,
            placeholder="Was ist passiert? Was hast du erwartet? Wie oft tritt es auf?")
        fb_submit = st.form_submit_button("📤 Einsenden", type="primary", use_container_width=True)

    if fb_submit and fb_titel.strip():
        ok = save_bug_report(
            typ=fb_typ,
            beschreibung=f"{fb_titel.strip()}\n\n{fb_beschr.strip()}",
            seite="profil-seite",
            user=uname,
        )
        if ok:
            st.success("✅ Feedback eingereicht — danke! Linus schaut sich das an.")
        else:
            st.error("Speichern fehlgeschlagen — GitHub-Verbindung prüfen.")
        st.rerun()
    elif fb_submit:
        st.error("Bitte einen Titel eingeben.")

    if my_feedback:
        st.divider()
        st.markdown(f"#### 📬 Meine Einreichungen ({len(my_feedback)})")
        status_color = {"offen":"#f97316","in Bearbeitung":"#3b82f6","erledigt":"#22c55e","abgelehnt":"#ef4444"}
        for fb in reversed(my_feedback):
            sc = status_color.get(fb.get("status","offen"),"#f97316")
            with st.expander(f"{fb['typ']} **{fb['titel']}**"):
                st.markdown(
                    f'<span style="background:{sc};color:white;padding:.18rem .6rem;border-radius:99px;'
                    f'font-size:.73rem;font-weight:600">{fb.get("status","offen").upper()}</span> '
                    f'<span style="font-size:.75rem;color:#57534e">· {fb.get("timestamp","?")[:10]} · '
                    f'Priorität: {fb.get("prioritaet","?")}</span>',
                    unsafe_allow_html=True)
                if fb.get("beschreibung"): st.markdown(fb["beschreibung"])

# ════════════════════════════════════════════════════════════════
# TAB 4: ADMIN (nur wenn Admin)
# ════════════════════════════════════════════════════════════════
if is_admin() and len(TABS) > 3:
    with TABS[3]:
        st.markdown("### 🛡️ Admin-Panel")
        admin_tabs = st.tabs(["👥 Nutzer", "📬 Feedback", "📊 System"])

        with admin_tabs[0]:
            st.markdown("#### 👥 Nutzerverwaltung")
            users = list_users()
            if users:
                st.dataframe(
                    [{k:v for k,v in u.items() if k != "pw_hash"} for u in users],
                    use_container_width=True, hide_index=True)
            col_p, col_b = st.columns(2)
            with col_p:
                promote_uname = st.text_input("Nutzer zu Admin befördern")
                if st.button("👑 Befördern", type="primary"):
                    ok, msg = promote_to_admin(promote_uname)
                    st.success(msg) if ok else st.error(msg)

        with admin_tabs[1]:
            st.markdown("#### 📬 Alle Feedback-Einreichungen")
            all_fb = read_json(PATH_FEEDBACK(), default=[]) or []
            if not all_fb:
                st.info("Noch kein Feedback eingereicht.")
            else:
                # Filter
                col_sf, col_sf2 = st.columns(2)
                with col_sf: f_status = st.multiselect("Status", ["offen","in Bearbeitung","erledigt","abgelehnt"], default=["offen","in Bearbeitung"])
                with col_sf2: f_typ = st.multiselect("Typ", list({fb["typ"] for fb in all_fb}))
                visible_fb = [fb for fb in all_fb if (not f_status or fb.get("status","offen") in f_status) and (not f_typ or fb.get("typ") in f_typ)]
                st.caption(f"{len(visible_fb)}/{len(all_fb)} Einträge")
                status_color = {"offen":"#f97316","in Bearbeitung":"#3b82f6","erledigt":"#22c55e","abgelehnt":"#ef4444"}
                for i,fb in enumerate(reversed(visible_fb)):
                    sc = status_color.get(fb.get("status","offen"),"#f97316")
                    with st.expander(f"{fb['typ']} **{fb['titel']}** · {fb.get('display_name','?')} · {fb.get('timestamp','?')[:10]}"):
                        c1,c2 = st.columns([3,1])
                        with c1:
                            st.markdown(f'<span style="background:{sc};color:white;padding:.18rem .6rem;border-radius:99px;font-size:.73rem;font-weight:600">{fb.get("status","?").upper()}</span>', unsafe_allow_html=True)
                            if fb.get("beschreibung"): st.markdown(fb["beschreibung"])
                        with c2:
                            new_status = st.selectbox("Status ändern", ["offen","in Bearbeitung","erledigt","abgelehnt"],
                                                       index=["offen","in Bearbeitung","erledigt","abgelehnt"].index(fb.get("status","offen")),
                                                       key=f"fb_status_{i}")
                            if st.button("💾 Speichern", key=f"fb_save_{i}"):
                                for j,x in enumerate(all_fb):
                                    if x.get("id") == fb.get("id"): all_fb[j]["status"] = new_status; break
                                write_json(PATH_FEEDBACK(), all_fb, commit_msg=f"update feedback status: {fb['id']}")
                                st.success("✅"); st.rerun()

        with admin_tabs[2]:
            st.markdown("#### 📊 System-Info")
            from src.config import MODEL_DEFAULT, MODEL_FAST, MODEL_HEAVY, MAX_MATERIAL_CHARS, get_secret
            from src.llm import HISTORY_LIMIT, MAX_MATERIAL_CONTEXT
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:.5rem">'
                + "".join([
                    f'<div style="background:white;border:1px solid #f0ede4;border-radius:8px;padding:.6rem .85rem">'
                    f'<div style="font-size:.67rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#57534e">{lbl}</div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:.82rem;font-weight:600;color:#1a2744">{val}</div></div>'
                    for lbl,val in [
                        ("Standard-Modell", MODEL_DEFAULT),
                        ("Korrektor-Modell", MODEL_HEAVY),
                        ("JSON-Modell (Haiku)", MODEL_FAST),
                        ("Chat-History Limit", f"{HISTORY_LIMIT} Nachrichten"),
                        ("Material-Kontext Max", f"{MAX_MATERIAL_CONTEXT:,} Zeichen"),
                        ("MASTER_BASE Tokens", "~350 (war ~2076, -84%)"),
                        ("Cache-Strategie", "System-Prompt first"),
                        ("Personas optimiert", "✓ Komprimiert"),
                    ]]) + '</div>',
                unsafe_allow_html=True)
