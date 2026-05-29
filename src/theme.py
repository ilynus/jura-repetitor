"""Design-System — Final.

Fixes gegenüber v5:
- Alle Sidebar-Texte WCAG AA konform (min. 4.5:1 Kontrastverhältnis)
- Body-Text #292524 statt #78716c
- Labels/Captions #44403c statt #78716c
- Nav-Links klar sichtbar, aktiver Link gold
- Konsistente Hover-States überall
"""
from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components


def apply_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --navy:       #1a2744;
  --navy-2:     #243460;
  --gold:       #c9a84c;
  --gold-2:     #e8c97b;
  --gold-3:     #f5e4a8;
  --parchment:  #faf8f3;
  --parchment-2:#edeae0;
  --ink:        #1c1917;
  --ink-2:      #292524;
  --ink-3:      #44403c;
  --ink-4:      #57534e;
  --r:10px; --r-sm:6px;
  --shadow-xs:0 1px 2px rgba(26,39,68,.07);
  --shadow-sm:0 1px 3px rgba(26,39,68,.09),0 2px 8px rgba(26,39,68,.06);
  --shadow:0 2px 8px rgba(26,39,68,.11),0 8px 24px rgba(26,39,68,.07);
  --t:.2s cubic-bezier(.4,0,.2,1);
}

/* ── BASE ── */
html,body,[data-testid="stAppViewContainer"]{
  font-family:'IBM Plex Sans',sans-serif!important;
  background:var(--parchment)!important;
  color:var(--ink-2)!important;
}
.main .block-container{padding-top:1.5rem!important;max-width:1280px!important;}
p,li,div{color:var(--ink-2);}

/* ── HEADINGS ── */
h1{font-family:'Playfair Display',serif!important;font-weight:700!important;
   color:var(--navy)!important;letter-spacing:-.025em!important;animation:fadeDown .4s ease both;}
h2{font-family:'Playfair Display',serif!important;font-weight:600!important;
   color:var(--navy)!important;animation:fadeDown .4s ease .04s both;}
h3{font-family:'IBM Plex Sans',sans-serif!important;font-weight:600!important;color:var(--navy-2)!important;}
code{font-family:'IBM Plex Mono',monospace!important;font-size:.85em!important;color:var(--navy)!important;
     background:rgba(26,39,68,.06)!important;padding:.05em .3em!important;border-radius:3px!important;}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{
  background:linear-gradient(175deg,#0f1a30 0%,#1a2744 55%,#1e2d5a 100%)!important;
  border-right:1px solid rgba(201,168,76,.18)!important;
}
/* KRITISCH: Alle Sidebar-Texte müssen lesbar sein */
[data-testid="stSidebar"] *{color:rgba(255,255,255,.92)!important;}
[data-testid="stSidebar"] .stCaption *,
[data-testid="stSidebar"] small{color:rgba(255,255,255,.72)!important;}

/* Nav-Links */
[data-testid="stSidebarNavLink"]{
  border-radius:var(--r-sm)!important;padding:.45rem .75rem!important;
  font-family:'IBM Plex Sans',sans-serif!important;font-weight:500!important;
  font-size:.875rem!important;color:rgba(255,255,255,.88)!important;
  transition:var(--t)!important;margin:.05rem 0!important;}
[data-testid="stSidebarNavLink"]:hover{
  background:rgba(255,255,255,.1)!important;color:white!important;}
[data-testid="stSidebarNavLink"][aria-selected="true"]{
  background:rgba(201,168,76,.18)!important;
  border-left:3px solid var(--gold)!important;
  color:var(--gold-2)!important;font-weight:600!important;}

/* Gruppen-Header */
[data-testid="stSidebarNavSectionHeader"]{
  color:rgba(255,255,255,.5)!important;font-size:.62rem!important;
  font-weight:700!important;letter-spacing:.1em!important;
  text-transform:uppercase!important;padding:.7rem .75rem .2rem!important;}

/* Sidebar-Buttons: ALLE States explizit weiß */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] .stButton button *,
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span{
  background:rgba(255,255,255,.08)!important;
  border:1px solid rgba(255,255,255,.2)!important;
  color:rgba(255,255,255,.95)!important;
  border-radius:var(--r-sm)!important;
  font-family:'IBM Plex Sans',sans-serif!important;
  font-weight:500!important;
  transition:var(--t)!important;}
[data-testid="stSidebar"] .stButton button:hover,
[data-testid="stSidebar"] .stButton button:hover *{
  background:rgba(201,168,76,.22)!important;
  border-color:rgba(201,168,76,.5)!important;
  color:white!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.1)!important;}
/* Sidebar Buttons explizit weiß */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] .stButton button *{
  color:rgba(255,255,255,.92)!important;}


/* ── METRICS ── */
[data-testid="stMetric"]{
  background:white!important;border:1px solid var(--parchment-2)!important;
  border-radius:var(--r)!important;padding:.85rem 1rem!important;
  box-shadow:var(--shadow-xs)!important;
  transition:box-shadow var(--t),transform var(--t)!important;animation:fadeUp .4s ease both;}
[data-testid="stMetric"]:hover{box-shadow:var(--shadow-sm)!important;transform:translateY(-2px)!important;}
[data-testid="stMetricLabel"]{font-size:.68rem!important;font-weight:700!important;
  letter-spacing:.07em!important;text-transform:uppercase!important;color:var(--ink-4)!important;}
[data-testid="stMetricValue"]{font-family:'Playfair Display',serif!important;
  color:var(--navy)!important;font-size:1.75rem!important;}

/* ── BUTTONS ── */
.stButton button[kind="primary"]{
  background:linear-gradient(135deg,var(--navy) 0%,var(--navy-2) 100%)!important;
  color:white!important;border:none!important;border-radius:var(--r-sm)!important;
  font-family:'IBM Plex Sans',sans-serif!important;font-weight:600!important;
  box-shadow:0 2px 8px rgba(26,39,68,.22)!important;transition:var(--t)!important;}
.stButton button[kind="primary"]:hover{
  box-shadow:0 4px 16px rgba(26,39,68,.3)!important;transform:translateY(-1px)!important;}
.stButton button:not([kind="primary"]){
  border-radius:var(--r-sm)!important;font-family:'IBM Plex Sans',sans-serif!important;
  color:#1c1917!important;border-color:#d6d3d1!important;
  background:white!important;transition:var(--t)!important;}
.stButton button:not([kind="primary"]):hover{
  border-color:#1a2744!important;color:#1a2744!important;background:#faf8f3!important;}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{border-bottom:2px solid var(--parchment-2)!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{
  font-family:'IBM Plex Sans',sans-serif!important;font-weight:500!important;
  font-size:.875rem!important;color:var(--ink-4)!important;
  padding:.5rem 1rem!important;border-bottom:2px solid transparent!important;
  margin-bottom:-2px!important;transition:var(--t)!important;}
.stTabs [aria-selected="true"]{
  color:var(--navy)!important;border-bottom-color:var(--gold)!important;font-weight:600!important;}
.stTabs [data-baseweb="tab"]:hover{color:var(--navy-2)!important;}

/* ── EXPANDER ── */
[data-testid="stExpander"]{
  border:1px solid var(--parchment-2)!important;border-radius:var(--r)!important;
  background:white!important;overflow:hidden!important;margin-bottom:.4rem!important;}
[data-testid="stExpander"]:hover{box-shadow:var(--shadow-xs)!important;}
[data-testid="stExpander"] summary{
  font-family:'IBM Plex Sans',sans-serif!important;font-weight:600!important;
  color:var(--navy)!important;font-size:.88rem!important;}

/* ── INPUTS ── */
.stTextInput input,.stTextArea textarea{
  font-family:'IBM Plex Sans',sans-serif!important;color:var(--ink-2)!important;
  border-radius:var(--r-sm)!important;border-color:var(--parchment-2)!important;
  background:white!important;transition:border-color var(--t),box-shadow var(--t)!important;}
.stTextInput input:focus,.stTextArea textarea:focus{
  border-color:var(--navy)!important;
  box-shadow:0 0 0 2px rgba(201,168,76,.2)!important;}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:var(--ink-4)!important;}
[data-testid="stWidgetLabel"] p{color:var(--ink-3)!important;font-weight:600!important;font-size:.82rem!important;}

/* ── SELECT / RADIO / CHECKBOX ── */
.stSelectbox [data-baseweb="select"] > div{
  border-color:var(--parchment-2)!important;border-radius:var(--r-sm)!important;background:white!important;}
.stRadio label,.stCheckbox label{color:var(--ink-2)!important;}

/* ── CHAT ── */
[data-testid="stChatMessage"]{border-radius:var(--r)!important;animation:fadeUp .3s ease both;}
[data-testid="stChatMessage"][data-testid*="assistant"]{
  background:white!important;border:1px solid var(--parchment-2)!important;}
[data-testid="stChatInput"]{border-radius:var(--r)!important;}
[data-testid="stChatInput"] *{color:var(--ink-2)!important;}

/* ── CONTAINERS ── */
[data-testid="stVerticalBlockBorderWrapper"]>div{
  border-radius:var(--r)!important;border-color:var(--parchment-2)!important;
  background:white!important;transition:box-shadow var(--t),transform var(--t)!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div:hover{
  box-shadow:var(--shadow-sm)!important;transform:translateY(-1px)!important;}

/* ── PROGRESS ── */
.stProgress>div>div>div>div{
  background:linear-gradient(90deg,var(--navy) 0%,var(--gold) 100%)!important;border-radius:99px!important;}
.stProgress>div>div{border-radius:99px!important;background:var(--parchment-2)!important;}

/* ── ALERTS ── */
[data-testid="stInfo"]{border-radius:var(--r)!important;border-left:3px solid var(--navy)!important;
  background:rgba(26,39,68,.04)!important;color:var(--ink-2)!important;}
[data-testid="stSuccess"]{border-radius:var(--r)!important;border-left:3px solid #15803d!important;color:var(--ink-2)!important;}
[data-testid="stWarning"]{border-radius:var(--r)!important;border-left:3px solid var(--gold)!important;color:var(--ink-2)!important;}
[data-testid="stError"]{border-radius:var(--r)!important;border-left:3px solid #dc2626!important;color:var(--ink-2)!important;}

/* ── CAPTIONS / KLEINE TEXTE ── */
.stCaption,[data-testid="stCaptionContainer"]{color:var(--ink-4)!important;font-size:.78rem!important;}

/* ── DIVIDER / SCROLLBAR ── */
hr{border-color:var(--parchment-2)!important;margin:1rem 0!important;}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--parchment)}
::-webkit-scrollbar-thumb{background:var(--navy-2);border-radius:99px}

/* ══════════════════════════════════
   GAMIFICATION
   ══════════════════════════════════ */

.xp-pill{
  display:inline-flex;align-items:center;gap:.35rem;
  background:linear-gradient(135deg,var(--navy),var(--navy-2));
  color:#f5e4a8!important;font-family:'IBM Plex Mono',monospace;
  font-size:.8rem;font-weight:600;padding:.28rem .75rem;border-radius:99px;
  border:1px solid rgba(201,168,76,.35);white-space:nowrap;
  box-shadow:0 1px 6px rgba(26,39,68,.2);}

.lvl-badge{
  display:inline-flex;align-items:center;gap:.3rem;
  background:linear-gradient(135deg,#b8860b,var(--gold),var(--gold-2));
  color:#1a2744!important;font-family:'Playfair Display',serif;
  font-size:.77rem;font-weight:700;padding:.25rem .68rem;border-radius:99px;
  box-shadow:0 2px 6px rgba(201,168,76,.3);}

.streak-badge{
  display:inline-flex;align-items:center;gap:.3rem;
  background:rgba(234,88,12,.12);color:#b45309!important;
  font-size:.78rem;font-weight:700;font-family:'IBM Plex Sans',sans-serif;
  padding:.25rem .68rem;border-radius:99px;border:1px solid rgba(234,88,12,.25);
  animation:pulseStreak 2.5s ease infinite;}

.xp-track{background:rgba(255,255,255,.15);border-radius:99px;height:6px;overflow:hidden;margin:.3rem 0;}
.xp-fill{height:100%;border-radius:99px;
  background:linear-gradient(90deg,rgba(201,168,76,.7),var(--gold-2));
  animation:growXP 1.2s cubic-bezier(.4,0,.2,1) both;}

/* ── Achievement-Karte ── */
.ach-card{display:flex;align-items:center;gap:.65rem;background:white;
  border:1px solid var(--parchment-2);border-radius:var(--r);
  padding:.65rem .9rem;box-shadow:var(--shadow-xs);transition:var(--t);
  animation:fadeUp .4s ease both;margin-bottom:.4rem;}
.ach-card:hover{box-shadow:var(--shadow-sm);transform:translateY(-1px);}
.ach-card.locked{opacity:.45;filter:grayscale(.8);}
.ach-icon{font-size:1.5rem;flex-shrink:0;}
.ach-name{font-weight:600;font-size:.84rem;color:var(--navy);}
.ach-desc{font-size:.73rem;color:var(--ink-4);margin-top:.1rem;}
.ach-xp{font-family:'IBM Plex Mono',monospace;font-size:.7rem;color:var(--gold);font-weight:600;margin-top:.15rem;}

/* ── Nav-Tile ── */
.nav-tile{background:white;border:1px solid var(--parchment-2);border-radius:var(--r);
  padding:1rem 1.15rem;box-shadow:var(--shadow-xs);
  transition:box-shadow var(--t),transform var(--t),border-color var(--t);
  animation:fadeUp .4s ease both;}
.nav-tile:hover{box-shadow:var(--shadow);transform:translateY(-3px);border-color:rgba(201,168,76,.4);}
.tile-icon{font-size:1.3rem;margin-bottom:.35rem;}
.tile-title{font-family:'Playfair Display',serif;font-weight:600;font-size:.9rem;color:var(--navy);margin-bottom:.25rem;}
.tile-desc{font-size:.76rem;color:var(--ink-4);line-height:1.45;}
.tile-xp{font-family:'IBM Plex Mono',monospace;font-size:.68rem;color:var(--gold);font-weight:600;margin-top:.4rem;}

/* ── Stat-Karte ── */
.stat-card{background:white;border:1px solid var(--parchment-2);border-radius:var(--r);
  padding:1rem 1.15rem;box-shadow:var(--shadow-xs);
  transition:box-shadow var(--t),transform var(--t);animation:fadeUp .4s ease both;}
.stat-card:hover{box-shadow:var(--shadow-sm);transform:translateY(-2px);}
.stat-icon{font-size:1.2rem;margin-bottom:.35rem;}
.stat-num{font-family:'Playfair Display',serif;font-size:1.85rem;font-weight:700;color:var(--navy);line-height:1.1;}
.stat-lbl{font-size:.66rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-4);margin-top:.1rem;}

/* ── Gold-Divider ── */
.gold-hr{height:1px;background:linear-gradient(90deg,transparent,var(--gold) 25%,var(--gold) 75%,transparent);
  border:none;margin:1rem 0;opacity:.35;}

/* ── Section-Header ── */
.sec-hdr{font-size:.67rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-4);
  display:flex;align-items:center;gap:.5rem;margin:.65rem 0 .5rem;}
.sec-hdr::after{content:'';flex:1;height:1px;background:var(--parchment-2);}

/* ── Due-Dot ── */
.due-dot{width:7px;height:7px;border-radius:50%;background:#d97706;
  display:inline-block;animation:pulseDot 2s ease infinite;}

/* ── Todo ── */
.todo-item{display:flex;align-items:center;gap:.6rem;padding:.45rem .75rem;
  background:white;border:1px solid var(--parchment-2);border-radius:var(--r-sm);
  margin-bottom:.3rem;transition:var(--t);}
.todo-item.done{opacity:.5;text-decoration:line-through;}
.todo-prio-high{border-left:3px solid #dc2626!important;}
.todo-prio-med{border-left:3px solid var(--gold)!important;}
.todo-prio-low{border-left:3px solid #22c55e!important;}

/* ── Badges ── */
.src-shared{background:#dbeafe;color:#1e40af!important;font-size:.73rem;font-weight:600;
  padding:.14rem .55rem;border-radius:99px;border:1px solid rgba(59,130,246,.2);}
.src-personal{background:#dcfce7;color:#14532d!important;font-size:.73rem;font-weight:600;
  padding:.14rem .55rem;border-radius:99px;border:1px solid rgba(34,197,94,.2);}

/* ── KEYFRAMES ── */
@keyframes fadeDown{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes growXP{from{width:0!important}}
@keyframes pulseDot{0%,100%{box-shadow:0 0 0 0 rgba(217,119,6,.35)}50%{box-shadow:0 0 0 5px rgba(217,119,6,0)}}
@keyframes pulseStreak{0%,100%{box-shadow:0 0 0 0 rgba(234,88,12,.2)}50%{box-shadow:0 0 0 4px rgba(234,88,12,0)}}

[data-testid="stMetric"]:nth-child(1){animation-delay:.04s}
[data-testid="stMetric"]:nth-child(2){animation-delay:.08s}
[data-testid="stMetric"]:nth-child(3){animation-delay:.12s}
[data-testid="stMetric"]:nth-child(4){animation-delay:.16s}
</style>
"""


# ── HTML-Helfer ──────────────────────────────────────────────────

def gold_divider() -> None:
    st.markdown('<hr class="gold-hr">', unsafe_allow_html=True)

def section_header(icon: str, text: str) -> None:
    st.markdown(f'<div class="sec-hdr">{icon} {text}</div>', unsafe_allow_html=True)

def stat_card(icon: str, num: str, label: str, delay: float = 0) -> str:
    return (f'<div class="stat-card" style="animation-delay:{delay}s">'
            f'<div class="stat-icon">{icon}</div>'
            f'<div class="stat-num">{num}</div>'
            f'<div class="stat-lbl">{label}</div></div>')

def nav_tile(icon: str, title: str, desc: str, xp_hint: str = "", delay: float = 0) -> str:
    xp = f'<div class="tile-xp">⚡ {xp_hint}</div>' if xp_hint else ""
    return (f'<div class="nav-tile" style="animation-delay:{delay}s">'
            f'<div class="tile-icon">{icon}</div>'
            f'<div class="tile-title">{title}</div>'
            f'<div class="tile-desc">{desc}</div>'
            f'{xp}</div>')

def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    st.markdown(
        f"""<div style="margin-bottom:.75rem">
        <h1 style="margin-bottom:.1rem">{icon + ' ' if icon else ''}{title}</h1>
        {f'<p style="font-size:.85rem;color:#57534e;margin:0">{subtitle}</p>' if subtitle else ''}
        </div>""",
        unsafe_allow_html=True,
    )

def render_top_bar(display_name: str, xp: int, level_name: str, level_icon: str) -> None:
    components.html(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
        <div style="width:100%;background:linear-gradient(90deg,#1a2744 0%,#243460 60%,#1e2d5a 100%);
          border-bottom:1px solid rgba(201,168,76,.2);padding:.42rem 1.2rem;
          display:flex;align-items:center;justify-content:space-between;
          box-shadow:0 2px 10px rgba(26,39,68,.18);box-sizing:border-box;">
          <div style="font-family:'IBM Plex Sans',sans-serif;font-weight:600;
            font-size:.8rem;color:rgba(255,255,255,.9)">🎓 Examensbegleiter</div>
          <div style="display:flex;align-items:center;gap:.65rem">
            <span style="background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);
              border-radius:99px;padding:.16rem .65rem;font-family:'IBM Plex Mono',monospace;
              font-size:.73rem;color:#e8c97b;font-weight:600">{level_icon} {level_name}</span>
            <span style="background:rgba(201,168,76,.15);border:1px solid rgba(201,168,76,.28);
              border-radius:99px;padding:.16rem .65rem;font-family:'IBM Plex Mono',monospace;
              font-size:.73rem;color:#e8c97b;font-weight:600">⚡ {xp:,} XP</span>
          </div>
          <div style="display:flex;align-items:center;gap:.85rem">
            <span style="font-family:'IBM Plex Sans',sans-serif;font-size:.76rem;
              color:rgba(255,255,255,.82)">👤 {display_name}</span>
            <span id="tbtime" style="font-family:'IBM Plex Mono',monospace;font-size:.74rem;
              color:rgba(255,255,255,.55);min-width:5rem;text-align:right">--:--:--</span>
          </div>
        </div>
        <script>
        (function(){{
          function pad(n){{return String(n).padStart(2,'0')}}
          function tick(){{var n=new Date(),t=document.getElementById('tbtime');
            if(t)t.textContent=pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds());}}
          tick();setInterval(tick,1000);
        }})();
        </script>""",
        height=44, scrolling=False,
    )






# ── BUG-BUTTON (Stub - wird in app.py Sidebar eingebunden) ───

def render_bug_button() -> None:
    """Leer - Bug-Meldung läuft über die Sidebar."""
    pass
