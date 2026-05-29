"""Wiederverwendbare UI-Komponenten.

Alle Komponenten erzeugen HTML das via st.markdown(unsafe_allow_html=True)
oder st.components.v1.html() eingebunden wird.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


# ---------------------------------------------------------------- #
#  LIVE-UHR (JavaScript, aktualisiert jede Sekunde)
# ---------------------------------------------------------------- #

def render_clock(height: int = 60) -> None:
    """Rendert eine Live-Uhr mit Datum und Uhrzeit.

    Nutzt st.components.v1.html() für echtes JavaScript.
    """
    clock_html = """
    <div id="clock-wrap" style="
      display: flex;
      align-items: baseline;
      gap: 1rem;
      padding: 0.4rem 1rem;
      background: linear-gradient(135deg, #1a2744 0%, #243460 100%);
      border-radius: 10px;
      border: 1px solid rgba(201,168,76,.25);
      box-shadow: 0 2px 12px rgba(26,39,68,.2);
      width: fit-content;
    ">
      <div id="clock-time" style="
        font-family: 'IBM Plex Mono', 'Courier New', monospace;
        font-size: 1.55rem;
        font-weight: 500;
        color: #e8c97b;
        letter-spacing: 0.05em;
        min-width: 7.5rem;
        text-align: center;
      ">--:--:--</div>
      <div id="clock-date" style="
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.82rem;
        font-weight: 400;
        color: rgba(255,255,255,.7);
        letter-spacing: 0.02em;
      ">Laden...</div>
    </div>
    <script>
      (function() {
        const DAYS = ['So','Mo','Di','Mi','Do','Fr','Sa'];
        const MONTHS = ['Jan','Feb','Mär','Apr','Mai','Jun',
                        'Jul','Aug','Sep','Okt','Nov','Dez'];
        function pad(n) { return String(n).padStart(2,'0'); }
        function tick() {
          const now = new Date();
          const h = pad(now.getHours());
          const m = pad(now.getMinutes());
          const s = pad(now.getSeconds());
          const day = DAYS[now.getDay()];
          const date = now.getDate();
          const month = MONTHS[now.getMonth()];
          const year = now.getFullYear();
          const t = document.getElementById('clock-time');
          const d = document.getElementById('clock-date');
          if (t) t.textContent = h + ':' + m + ':' + s;
          if (d) d.textContent = day + ', ' + pad(date) + '. ' + month + ' ' + year;
        }
        tick();
        setInterval(tick, 1000);
      })();
    </script>
    """
    components.html(clock_html, height=height, scrolling=False)


# ---------------------------------------------------------------- #
#  XP-TOAST (flüchtige Erfolgsmeldung)
# ---------------------------------------------------------------- #

def show_xp_toast(earned: int, action_label: str = "") -> None:
    """Zeigt einen kurzen XP-Toast via st.toast()."""
    if earned > 0:
        suffix = f" — {action_label}" if action_label else ""
        st.toast(f"✨ +{earned} XP{suffix}", icon="⚡")


# ---------------------------------------------------------------- #
#  FORTSCHRITTSBALKEN (custom, animiert)
# ---------------------------------------------------------------- #

def render_xp_bar(progress: float, label: str = "") -> None:
    """Rendert einen animierten XP-Fortschrittsbalken (0.0–1.0)."""
    pct = int(max(0, min(progress, 1.0)) * 100)
    st.markdown(
        f"""
        <div style="margin:0.25rem 0">
          {'<div style="font-size:.75rem;color:#78716c;margin-bottom:.2rem">' + label + '</div>' if label else ''}
          <div class="xp-bar-wrap">
            <div class="xp-bar-fill" style="width:{pct}%"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- #
#  STAT-KARTEN (4er-Reihe)
# ---------------------------------------------------------------- #

def render_stat_row(stats: list[tuple[str, str, str]], delays: list[float] | None = None) -> None:
    """Rendert eine Reihe von Statistik-Karten.

    stats: [(icon, value, label), ...]
    """
    cols = st.columns(len(stats))
    for i, (icon, value, label) in enumerate(stats):
        delay = (delays[i] if delays else i * 0.07)
        with cols[i]:
            st.markdown(
                f"""
                <div class="stat-card" style="animation-delay:{delay}s">
                  <div class="stat-icon">{icon}</div>
                  <div class="stat-number">{value}</div>
                  <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------- #
#  QUELLE-BADGES
# ---------------------------------------------------------------- #

def source_badge_html(source_type: str) -> str:
    """Gibt HTML für einen Quell-Badge zurück."""
    from src.config import SOURCE_TYPE_SHARED
    style = "shared" if source_type == SOURCE_TYPE_SHARED else "personal"
    label = "🔵 Gemeinsam" if source_type == SOURCE_TYPE_SHARED else "🟢 Persönlich"
    return f'<span class="src-badge {style}">{label}</span>'


def render_source_badge(source_type: str) -> None:
    """Streamt einen Quell-Badge direkt in die Streamlit-UI."""
    st.markdown(source_badge_html(source_type), unsafe_allow_html=True)


# ---------------------------------------------------------------- #
#  GOLD-DIVIDER
# ---------------------------------------------------------------- #

def gold_divider() -> None:
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------------- #
#  SECTION-HEADER
# ---------------------------------------------------------------- #

def section_header(icon: str, title: str) -> None:
    st.markdown(
        f'<div class="section-header">{icon} {title}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- #
#  FÄLLIG-INDIKATOR
# ---------------------------------------------------------------- #

def due_indicator(n: int) -> None:
    """Zeigt einen pulsierenden 'Heute fällig'-Hinweis."""
    if n > 0:
        st.markdown(
            f'<span class="due-pulse">⏰ {n} Karte{"n" if n != 1 else ""} heute fällig</span>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------- #
#  WELCOME-BANNER (animierter Header)
# ---------------------------------------------------------------- #

def welcome_banner(display_name: str, subtitle: str = "") -> None:
    """Animierter Willkommens-Header."""
    st.markdown(
        f"""
        <div style="animation: fadeSlideDown 0.5s ease both;">
          <h1 style="margin-bottom:.1rem">
            🎓 Examensbegleiter NRW
          </h1>
          <p style="
            font-family:'IBM Plex Sans',sans-serif;
            font-size:.95rem;
            color:#78716c;
            margin:0 0 .75rem;
            animation: fadeIn 0.6s ease 0.2s both;
          ">
            Willkommen, <strong style="color:#1a2744">{display_name}</strong>
            {' &mdash; ' + subtitle if subtitle else ''}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
