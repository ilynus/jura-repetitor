"""Bug-Reporter — empfängt Meldungen aus dem floating Widget und speichert sie.

Das Widget sendet via sessionStorage. Streamlit fragt bei jedem Rerun ab
ob ein neuer Report vorliegt. Gespeichert wird in PATH_FEEDBACK (shared →
Admin sieht alle).
"""
from __future__ import annotations
import json
import uuid
import datetime as dt
import streamlit as st
import streamlit.components.v1 as components

from src.config import PATH_FEEDBACK
from src.github_db import read_json, write_json, now_iso


def render_bug_receiver() -> None:
    """Unsichtbare Komponente: liest sessionStorage, speichert Bug-Reports.
    
    Auf jeder Page einbinden — funktioniert zusammen mit render_bug_button().
    """
    # JS liest sessionStorage und schickt Daten via Streamlit-Query
    receiver_html = """
    <script>
    (function(){
      var report = null;
      try{ report = sessionStorage.getItem('bug_report'); }catch(e){}
      if(report){
        try{ sessionStorage.removeItem('bug_report'); }catch(e){}
        // An Streamlit via URL übergeben
        var url = new URL(window.parent.location.href);
        url.searchParams.set('bug_report', report);
        // Nicht navigieren, nur Streamlit-State setzen via postMessage
        window.parent.postMessage({
          type: 'streamlit:setComponentValue',
          value: report
        }, '*');
      }
    })();
    </script>
    """
    result = components.html(receiver_html, height=0, scrolling=False)

    # Alternativ: direktes st.session_state-basiertes Formular
    # das als unsichtbares Overlay funktioniert
    _check_and_save_pending()


def _check_and_save_pending() -> None:
    """Speichert ausstehende Bug-Reports aus st.session_state."""
    pending = st.session_state.pop("pending_bug_report", None)
    if pending:
        _save_report(pending)


def save_bug_report(typ: str, beschreibung: str, seite: str = "", user: str = "anonym") -> bool:
    """Speichert einen Bug-Report direkt (für das Profil-Formular)."""
    return _save_report({
        "typ": typ,
        "beschreibung": beschreibung,
        "seite": seite,
        "user": user,
        "timestamp": now_iso(),
        "quelle": "profil-seite",
    })


def _save_report(report: dict) -> bool:
    report.setdefault("id", str(uuid.uuid4())[:8])
    report.setdefault("status", "offen")
    report.setdefault("user", st.session_state.get("auth_user", {}).get("username", "anonym"))

    all_reports = read_json(PATH_FEEDBACK(), default=[]) or []
    all_reports.append(report)
    return write_json(
        PATH_FEEDBACK(), all_reports,
        commit_msg=f"bug: {report.get('typ','?')} — {str(report.get('beschreibung',''))[:40]}"
    )
