"""Materialien & Projekte — Upload, Handschrift-OCR, Lernprojekte."""
from __future__ import annotations
import base64, json, uuid, datetime as dt
from pathlib import Path
import streamlit as st

from src import personas
from src.auth import is_admin, require_login
from src.config import (PATH_MATERIALS, PATH_SHARED_MATERIALS, SOURCE_BADGE,
                        SOURCE_COLOR, SOURCE_TYPE_PERSONAL, SOURCE_TYPE_SHARED, personal_path)
from src.document_loader import extract_text
from src.github_db import read_json, write_json, now_iso
from src.llm import chat_complete, json_complete, vision_stream
from src.score import award_xp, get_level_info, get_score, show_xp_toast
from src.theme import apply_theme, gold_divider, page_header, render_top_bar

apply_theme()
user = require_login()
uname = user["username"]
score_data = get_score(uname)
xp = score_data.get("xp", 0)
info = get_level_info(xp)
render_top_bar(user["display_name"], xp, info["name"], info["icon"])
page_header("Materialien & Projekte", "Upload · Handschrift-OCR · Lernprojekte", "📂")

TABS = st.tabs(["📤 Materialien", "✏️ Handschrift → Skript", "📂 Lernprojekte"])

# ════════════════════════════════════════════════════════════════
# TAB 1: MATERIALIEN
# ════════════════════════════════════════════════════════════════
with TABS[0]:
    def _load_all():
        shared = read_json(PATH_SHARED_MATERIALS(), default=[]) or []
        personal = read_json(PATH_MATERIALS(), default=[]) or []
        for m in shared: m.setdefault("source_type", SOURCE_TYPE_SHARED)
        for m in personal: m.setdefault("source_type", SOURCE_TYPE_PERSONAL)
        return shared, personal

    def _badge(src):
        color = SOURCE_COLOR.get(src, "#f0ede4")
        label = SOURCE_BADGE.get(src, "?")
        return f'<span style="background:{color};padding:2px 8px;border-radius:10px;font-size:.76rem;font-weight:600">{label}</span>'

    sub_m = st.tabs(["➕ Hochladen", "📚 Übersicht", "🗺️ Quellenmatrix"])

    with sub_m[0]:
        st.markdown("#### Neues Material hinzufügen")
        target = st.radio("Wohin?", [
            f"{SOURCE_BADGE[SOURCE_TYPE_PERSONAL]} — nur für mich",
            f"{SOURCE_BADGE[SOURCE_TYPE_SHARED]} — für alle (nur Admins)"
        ], horizontal=True)
        upload_shared = "Gemeinsam" in target
        if upload_shared and not is_admin():
            st.warning("⚠️ Nur Admins dürfen gemeinsame Materialien hochladen.")
        else:
            uploaded = st.file_uploader("PDF, DOCX, TXT oder MD", type=["pdf","docx","txt","md"])
            c1,c2 = st.columns(2)
            with c1: topic = st.text_input("Rechtsgebiet", placeholder="z.B. SchuldR BT")
            with c2: art = st.selectbox("Art", ["Skript","Vorlesungsmitschrift","AG-Fall","Kommentarauszug","Lehrbuchauszug","Eigene Notizen","Sonstiges"])
            if st.button("➕ Hochladen", type="primary", disabled=uploaded is None):
                try:
                    name, text, pages = extract_text(uploaded)
                    if not text.strip(): st.error("Kein Text extrahierbar.")
                    else:
                        entry = {"name":name,"topic":topic.strip() or None,"art":art,
                                 "text":text,"chars":len(text),"pages":pages,
                                 "uploader":uname,"source_type":SOURCE_TYPE_SHARED if upload_shared else SOURCE_TYPE_PERSONAL}
                        if upload_shared:
                            mats = [m for m in (read_json(PATH_SHARED_MATERIALS(), default=[]) or []) if m["name"] != name] + [entry]
                            write_json(PATH_SHARED_MATERIALS(), mats, commit_msg=f"[shared] add: {name}")
                        else:
                            mats = [m for m in (read_json(PATH_MATERIALS(), default=[]) or []) if m["name"] != name] + [entry]
                            write_json(PATH_MATERIALS(), mats, commit_msg=f"add: {name}")
                        e = award_xp("material", note=name); show_xp_toast(e, "Material hochgeladen")
                        st.success(f"✅ {name} gespeichert ({len(text):,} Zeichen, {pages} Seiten).")
                        st.rerun()
                except ValueError as ex: st.error(str(ex))
                except Exception as ex: st.error(f"Fehler: {ex}")

    with sub_m[1]:
        shared_mats, personal_mats = _load_all()
        all_mats = shared_mats + personal_mats
        c1,c2,c3 = st.columns(3)
        c1.metric("Gesamt", len(all_mats))
        c2.metric("🔵 Gemeinsam", len(shared_mats))
        c3.metric("🟢 Persönlich", len(personal_mats))
        st.divider()
        col_sh, col_pe = st.columns(2)
        for col, mats, src, editable in [(col_sh, shared_mats, SOURCE_TYPE_SHARED, is_admin()),
                                          (col_pe, personal_mats, SOURCE_TYPE_PERSONAL, True)]:
            with col:
                st.markdown(_badge(src) + f" **{len(mats)} Dateien**", unsafe_allow_html=True)
                if not mats: st.caption("Keine Materialien.")
                for i,m in enumerate(mats):
                    with st.expander(m["name"]):
                        st.markdown(_badge(m.get("source_type",src)), unsafe_allow_html=True)
                        st.caption(f"{m.get('chars',0):,} Zeichen · {m.get('pages',1)} Seiten · {m.get('art','?')} · {m.get('topic','—')}")
                        preview = m.get("text","")[:1500]
                        st.text_area("", value=preview + ("..." if len(m.get("text","")) > 1500 else ""),
                                     height=150, key=f"prev_{src}_{i}", disabled=True, label_visibility="collapsed")
                        if editable and st.button("🗑️ Löschen", key=f"del_{src}_{i}"):
                            if src == SOURCE_TYPE_SHARED:
                                updated = [x for x in shared_mats if x["name"] != m["name"]]
                                write_json(PATH_SHARED_MATERIALS(), updated, commit_msg=f"remove: {m['name']}")
                            else:
                                updated = [x for x in personal_mats if x["name"] != m["name"]]
                                write_json(PATH_MATERIALS(), updated, commit_msg=f"remove: {m['name']}")
                            st.rerun()

    with sub_m[2]:
        st.markdown("#### 🗺️ Quellenmatrix")
        st.caption("KI analysiert alle Materialien und erkennt Doppelungen und Lücken.")
        shared_mats, personal_mats = _load_all()
        all_for_matrix = shared_mats + personal_mats
        if not all_for_matrix: st.info("Keine Materialien vorhanden.")
        elif st.button("🧠 Quellenmatrix generieren", type="primary"):
            user_msg = "Erstelle Quellenmatrix:\n\n" + "\n\n".join(
                f"### [{m.get('source_type','?').upper()}] {m['name']}\nArt:{m.get('art','?')} Rechtsgebiet:{m.get('topic','?')}\n{m['text'][:3000]}"
                for m in all_for_matrix)
            with st.spinner("Analysiere (Haiku)..."):
                raw = json_complete(user_msg, personas.QUELLENMATRIX_GENERATOR, max_tokens=2000)
            try:
                data = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
                entries = data.get("entries", [])
                if entries: st.dataframe(entries, use_container_width=True, hide_index=True)
                if data.get("doppelungen"):
                    st.markdown("#### 🔁 Doppelungen")
                    for d in data["doppelungen"]: st.markdown(f"- {d}")
                if data.get("luecken"):
                    st.markdown("#### 🕳️ Lücken")
                    for l in data["luecken"]: st.markdown(f"- {l}")
            except: st.error("Fehler."); st.code(raw)

# ════════════════════════════════════════════════════════════════
# TAB 2: HANDSCHRIFT → SKRIPT
# ════════════════════════════════════════════════════════════════
with TABS[1]:
    st.markdown("#### ✏️ Handschrift-OCR")
    with st.expander("ℹ️ Anleitung"):
        st.markdown("Foto oder Scan hochladen → Claude transkribiert → bereinigt → ergänzt examensnah. Eigene Ergänzungen werden mit 💡 markiert.")
    uploaded_imgs = st.file_uploader("Seiten hochladen (JPG, PNG, WEBP)", type=["jpg","jpeg","png","webp"], accept_multiple_files=True)
    if uploaded_imgs:
        try:
            from PIL import Image as PILImage
        except ImportError:
            PILImage = None
        cols_prev = st.columns(min(len(uploaded_imgs), 4))
        for i,f in enumerate(uploaded_imgs):
            if PILImage:
                img = PILImage.open(f)
                cols_prev[i%4].image(img, caption=f.name, use_container_width=True)
            else:
                cols_prev[i%4].image(f, caption=f.name, use_container_width=True)
            f.seek(0)
        c1,c2 = st.columns(2)
        with c1:
            topic_hw = st.text_input("Rechtsgebiet", placeholder="z.B. BGB AT")
            mat_name_hw = st.text_input("Name des fertigen Skripts", value=f"Handschrift_{topic_hw or 'Skript'}.md")
        with c2:
            ergaenzungen = st.checkbox("Examensrelevante Ergänzungen", value=True)
            save_target = st.radio("Speichern als", ["🟢 Persönlich","🔵 Gemeinsam (Admin)"], horizontal=True)
            save_shared_hw = "Gemeinsam" in save_target and is_admin()
        if st.button("🔍 Verarbeiten", type="primary", use_container_width=True):
            all_pages = []
            pb = st.progress(0, "Verarbeite Seiten...")
            for i,f in enumerate(uploaded_imgs):
                f.seek(0); raw_bytes = f.read()
                b64 = base64.b64encode(raw_bytes).decode()
                suffix = Path(f.name).suffix.lower()
                mt_map = {".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png",".webp":"image/webp"}
                media_type = mt_map.get(suffix, "image/jpeg")
                prompt = (f"Verarbeite diese handgeschriebene Seite.\n"
                          + (f"Rechtsgebiet: {topic_hw}\n" if topic_hw else "")
                          + ("Examensrelevante Ergänzungen mit 💡 markieren." if ergaenzungen else "Nur Transkription und Bereinigung."))
                st.markdown(f"--- \n#### 📄 Seite {i+1}")
                with st.chat_message("assistant"):
                    page_result = st.write_stream(vision_stream(b64, media_type, prompt, personas.HANDSCHRIFT_VERBESSERER))
                all_pages.append(page_result)
                pb.progress((i+1)/len(uploaded_imgs))
            pb.empty()
            full_text = "\n\n---\n\n".join(all_pages)
            st.download_button("⬇️ Als Markdown herunterladen", full_text,
                               mat_name_hw if mat_name_hw.endswith(".md") else mat_name_hw+".md", "text/markdown")
            if st.button("💾 Als Material speichern"):
                entry = {"name":mat_name_hw or "Handschrift.md","topic":topic_hw or None,
                         "art":"Handschrift (digitalisiert)","text":full_text[:200_000],
                         "chars":len(full_text),"pages":len(uploaded_imgs),
                         "uploader":uname,
                         "source_type":SOURCE_TYPE_SHARED if save_shared_hw else SOURCE_TYPE_PERSONAL}
                if save_shared_hw:
                    mats = (read_json(PATH_SHARED_MATERIALS(), default=[]) or []) + [entry]
                    write_json(PATH_SHARED_MATERIALS(), mats, commit_msg=f"[shared] handwriting: {mat_name_hw}")
                else:
                    mats = (read_json(PATH_MATERIALS(), default=[]) or []) + [entry]
                    write_json(PATH_MATERIALS(), mats, commit_msg=f"handwriting: {mat_name_hw}")
                e = award_xp("handwriting", note=mat_name_hw); show_xp_toast(e)
                st.success("✅ Als Material gespeichert.")

# ════════════════════════════════════════════════════════════════
# TAB 3: LERNPROJEKTE
# ════════════════════════════════════════════════════════════════
with TABS[2]:
    def _idx_path(): return personal_path("projects","_index.json")
    def _meta_path(pid): return personal_path("projects",pid,"meta.json")
    def _struct_path(pid): return personal_path("projects",pid,"structure.json")
    def _sources_path(pid): return personal_path("projects",pid,"sources.json")
    def _chat_path(pid): return personal_path("projects",pid,"chat.json")
    def _load_projects(): return read_json(_idx_path(), default=[]) or []
    def _save_projects(p): write_json(_idx_path(), p, commit_msg="update projects")

    projects = _load_projects()
    col_nav, col_new = st.columns([3,1])
    with col_nav:
        labels = ["➕ Neues Projekt erstellen"] + [f"{'📚' if p['typ']=='Lernprojekt' else '🔬'} {p['titel']}" for p in projects]
        sel = st.selectbox("Projekt", labels)
        active = None if sel.startswith("➕") else projects[labels.index(sel)-1]
    with col_new:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Neu", use_container_width=True): active = None

    if active is None:
        st.divider()
        st.markdown("### ➕ Neues Projekt")
        with st.form("new_proj"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                proj_typ = st.radio("Typ", ["📚 Lernprojekt","🔬 Wissenschaftliche Arbeit"])
                proj_titel = st.text_input("Titel *", placeholder="Examensvorbereitung Sachenrecht")
            with col_p2:
                proj_thema = st.text_area("Thema", height=80, placeholder="Was soll erarbeitet werden?")
                proj_deadline = st.date_input("Deadline", value=None, min_value=dt.date.today())
            rechtsgebiete = st.multiselect("Rechtsgebiete", ["BGB AT","SchuldR AT","SchuldR BT","SachenR","StrafR AT","StrafR BT","GR","AllgVerwR"])
            shared_m, personal_m = (read_json(PATH_SHARED_MATERIALS(),default=[]) or []), (read_json(PATH_MATERIALS(),default=[]) or [])
            all_m = shared_m + personal_m
            sel_mats = st.multiselect("Materialien verknüpfen", [m["name"] for m in all_m])
            create_btn = st.form_submit_button("🚀 Erstellen & Struktur generieren", type="primary", use_container_width=True)
        if create_btn and proj_titel.strip():
            typ_clean = "Wissenschaftliche Arbeit" if "Wissenschaftliche" in proj_typ else "Lernprojekt"
            pid = str(uuid.uuid4())[:8]
            mat_ctx = "\n".join(f"- {m['name']} ({m.get('topic','?')})" for m in all_m if m["name"] in sel_mats)
            struct_prompt = (
                f"{'Lernplan' if typ_clean=='Lernprojekt' else 'Inhaltsverzeichnis'} für:\n"
                f"Titel: {proj_titel}\nThema: {proj_thema}\nRechtsgebiete: {', '.join(rechtsgebiete)}\n"
                f"Deadline: {str(proj_deadline) if proj_deadline else 'keine'}\nMaterialien:\n{mat_ctx or 'keine'}\n\n"
                + ("Erstelle strukturierten Lernplan mit Phasen, Meilensteinen, Wiederholungszyklen." if typ_clean=="Lernprojekt"
                   else "Erstelle Inhaltsverzeichnis mit Einleitung/Hauptteil/Schluss, Quellenempfehlungen, wissenschaftliche Hinweise."))
            with st.spinner("Generiere Struktur..."):
                structure = chat_complete([{"role":"user","content":struct_prompt}], personas.PROJEKTLEKTOR, max_tokens=3000)
            meta = {"id":pid,"titel":proj_titel,"typ":typ_clean,"thema":proj_thema,"rechtsgebiete":rechtsgebiete,
                    "deadline":str(proj_deadline) if proj_deadline else None,"materialien":sel_mats,"status":"aktiv","erstellt":now_iso()}
            write_json(_meta_path(pid), meta, commit_msg=f"create project: {proj_titel}")
            write_json(_struct_path(pid), {"content":structure,"generated":now_iso()}, commit_msg=f"gen struct: {pid}")
            write_json(_sources_path(pid), [], commit_msg=f"init sources: {pid}")
            write_json(_chat_path(pid), [], commit_msg=f"init chat: {pid}")
            projects.append(meta); _save_projects(projects)
            award_xp("project", note=proj_titel)
            st.success(f"✅ Projekt '{proj_titel}' erstellt!")
            st.rerun()
    else:
        pid = active["id"]
        struct_data = read_json(_struct_path(pid), default={}) or {}
        sources = read_json(_sources_path(pid), default=[]) or []
        chat_history = read_json(_chat_path(pid), default=[]) or []
        proj_icon = "📚" if active["typ"] == "Lernprojekt" else "🔬"
        rg_html = "".join(
            f'<span style="background:rgba(255,255,255,.1);color:rgba(255,255,255,.8);'
            f'font-size:.72rem;padding:.15rem .5rem;border-radius:6px;margin-right:.3rem">{r}</span>'
            for r in active.get("rechtsgebiete", [])
        )
        dl_html = (f'&nbsp;·&nbsp;<span style="color:rgba(201,168,76,.8);font-size:.75rem">⏰ {active["deadline"]}</span>'
                   if active.get("deadline") else "")
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1a2744,#243460);border-radius:10px;'
            f'padding:1rem 1.25rem;margin-bottom:.75rem;border:1px solid rgba(201,168,76,.2)">'
            f'<div style="font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;color:white">'
            f'{proj_icon} {active["titel"]}</div>'
            f'<div style="color:rgba(255,255,255,.65);font-size:.82rem;margin-top:.2rem">{active.get("thema","")}</div>'
            f'<div style="margin-top:.4rem">{rg_html}{dl_html}</div>'
            f'</div>', unsafe_allow_html=True)
        pt1,pt2,pt3,pt4 = st.tabs(["📋 Struktur","📚 Materialien","📚 Quellen","🧑‍💼 Lektor"])
        with pt1:
            if struct_data.get("content"):
                st.markdown(struct_data["content"])
                st.download_button("⬇️ Als Markdown", struct_data["content"], f"struktur_{pid}.md", "text/markdown")
        with pt2:
            all_m = (read_json(PATH_SHARED_MATERIALS(),default=[]) or []) + (read_json(PATH_MATERIALS(),default=[]) or [])
            linked = [m for m in all_m if m["name"] in active.get("materialien",[])]
            unlinked = [m for m in all_m if m["name"] not in active.get("materialien",[])]
            c_l, c_u = st.columns(2)
            with c_l:
                st.markdown(f"**Im Projekt ({len(linked)})**")
                for m in linked:
                    st.markdown(f"- 📄 {m['name']}")
                    if st.button("Entfernen", key=f"unlink_{i}_{m['name'][:12]}"):
                        active["materialien"] = [n for n in active["materialien"] if n != m["name"]]
                        write_json(_meta_path(pid), active, commit_msg=f"unlink: {m['name']}"); st.rerun()
            with c_u:
                st.markdown(f"**Verfügbar ({len(unlinked)})**")
                for m in unlinked:
                    if st.button(f"➕ {m['name']}", key=f"link_{i}_{m['name'][:12]}"):
                        active.setdefault("materialien",[]).append(m["name"])
                        write_json(_meta_path(pid), active, commit_msg=f"link: {m['name']}"); st.rerun()
        with pt3:
            with st.expander("➕ Quelle hinzufügen"):
                with st.form("add_src"):
                    s_typ = st.selectbox("Typ", ["Kommentar","Lehrbuch","Aufsatz","Urteil","Gesetz","Internet","Sonstiges"])
                    sc1,sc2 = st.columns(2)
                    with sc1: s_autor = st.text_input("Autor", placeholder="Grüneberg, Christian")
                    with sc1: s_titel = st.text_input("Titel")
                    with sc2: s_jahr = st.text_input("Jahr/Auflage", placeholder="2024")
                    with sc2: s_kurz = st.text_input("Kurzbeleg (Fußnote)", placeholder="Grüneberg/Sprau, § 823 Rn. 45")
                    s_url = st.text_input("URL (optional)")
                    if st.form_submit_button("➕ Speichern", type="primary"):
                        sources.append({"id":str(uuid.uuid4())[:6],"typ":s_typ,"autor":s_autor,"titel":s_titel,
                                        "jahr":s_jahr,"kurzbeleg":s_kurz,"url":s_url,"added":now_iso()})
                        write_json(_sources_path(pid), sources, commit_msg=f"add source: {s_titel}"); st.rerun()
            if sources:
                sorted_s = sorted(sources, key=lambda x: x.get("autor","").split(",")[0].lower())
                st.markdown("**Literaturverzeichnis:**")
                bib = []
                for s in sorted_s:
                    line = f"{s.get('autor','')} — {s.get('titel','')} ({s.get('jahr','')})"
                    bib.append(line)
                    with st.expander(line):
                        if s.get("kurzbeleg"): st.markdown(f"Kurzbeleg: `{s['kurzbeleg']}`")
                        if s.get("url"): st.link_button("🔗 Öffnen", s["url"])
                        if st.button("🗑️", key=f"delsrc_{s['id']}"):
                            sources = [x for x in sources if x["id"] != s["id"]]
                            write_json(_sources_path(pid), sources, commit_msg="del source"); st.rerun()
                st.download_button("⬇️ Literaturverzeichnis", "\n\n".join(bib), f"lit_{pid}.md", "text/markdown")
        with pt4:
            st.markdown("**🧑‍💼 Projektlektor** — kennt dein Projekt, Materialien und Quellen.")
            src_liste = "\n".join(f"- {s.get('autor','?')}: {s.get('titel','?')}" for s in sources)
            lektor_sys = personas.PROJEKTLEKTOR + (
                f"\n\n# AKTUELLES PROJEKT\nTitel:{active['titel']}\nTyp:{active['typ']}\n"
                f"Thema:{active.get('thema','')}\nMaterialien:{', '.join(active.get('materialien',[]))}\n"
                f"Quellen:\n{src_liste or 'keine'}\nDeadline:{active.get('deadline','keine')}")
            for msg in chat_history:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            qcols = st.columns(3)
            quick = [("📊 Projektstand","Gib mir einen Überblick: Projektstand, nächste Schritte, Prioritäten."),
                     ("🔍 Lücken","Analysiere Struktur und Materialien: wo sind inhaltliche Lücken?"),
                     ("📅 Zeitplan",f"Erstelle Zeitplan bis Deadline {active.get('deadline','?')} mit Meilensteinen.")]
            for i,(label,prompt) in enumerate(quick):
                if qcols[i].button(label, use_container_width=True, key=f"lekt_{i}"):
                    chat_history.append({"role":"user","content":prompt}); write_json(_chat_path(pid), chat_history[-50:], commit_msg=f"lektor:{pid}"); st.rerun()
            user_in = st.chat_input("Frag den Projektlektor...")
            if user_in:
                chat_history.append({"role":"user","content":user_in})
                from src.llm import chat_stream
                with st.chat_message("assistant"):
                    resp = st.write_stream(chat_stream(chat_history, lektor_sys))
                chat_history.append({"role":"assistant","content":resp})
                write_json(_chat_path(pid), chat_history[-50:], commit_msg=f"lektor:{pid}"); st.rerun()
