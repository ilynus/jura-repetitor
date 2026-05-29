"""RSS-Fetcher für juristische News (LTO + weitere Quellen).

Korrekturen ggü. dem Ausgangs-Code:
- Alle Feed-URLs gegen lto.de/rss verifiziert (Mai 2026)
- Fehlerbehandlung beim Feed-Abruf (Netzwerkprobleme → leere Liste, kein Crash)
- Timezone-aware Sortierung: datetime.min war timezone-naiv → Crash, wenn
  Feed-Einträge tz-aware Datumswerte liefern. Fix: UTC-aware Fallback.
- Caching via @st.cache_data (TTL 30 min) — vermeidet bei jedem Rerun
  neue HTTP-Requests an LTO.
"""
from __future__ import annotations

import datetime as dt

import feedparser
import streamlit as st
from bs4 import BeautifulSoup


# ===========================================================
#  Verifizierte Feed-URLs (Stand: Mai 2026, lto.de/rss)
# ===========================================================
LTO_FEEDS: dict[str, str] = {
    # Allgemeine Rubriken
    "Nachrichten": "https://www.lto.de/nachrichten-rss/rss/feed.xml",
    "Studium & Referendariat": "https://www.lto.de/studium-referendariat-rss/rss/feed.xml",
    "Hintergründe": "https://www.lto.de/hintergruende-rss/rss/feed.xml",
    "Presseschau": "https://www.lto.de/presseschau-rss/rss/feed.xml",
    # Pflichtfach-Rechtsgebiete (mit verifizierten IDs)
    "Öffentliches Recht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=17",
    "Verwaltungsrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=111",
    "Polizei- und Ordnungsrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=109",
    "Staatsrecht / Staatsorganisation": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=108",
    "Strafrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=19",
    "Zivil- und Zivilverfahrensrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=25",
    "Arbeitsrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=26",
    "Handels- und Gesellschaftsrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=10",
    "Europa- und Völkerrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=08",
    "Erbrecht": "https://www.lto.de/rss/feed.xml?tx_ltorss_pi1[rechtsgebiet]=07",
}

# Standard-Auswahl beim App-Start (Pflichtfach-Rubriken)
DEFAULT_FEEDS = [
    "Nachrichten",
    "Öffentliches Recht",
    "Strafrecht",
    "Zivil- und Zivilverfahrensrecht",
    "Studium & Referendariat",
]

# Schlüsselwörter für examensrelevante Filterung
EXAM_KEYWORDS = frozenset([
    "bgh", "bundesgerichtshof",
    "bverfg", "bundesverfassungsgericht",
    "bverwg", "bundesverwaltungsgericht",
    "bag", "bundesarbeitsgericht",
    "bfh", "bundesfinanzhof",
    "bsg", "bundessozialgericht",
    "olg", "oberverwaltungsgericht", "ovg",
    "eugh", "egmr",
    "urteil", "beschluss", "revision",
    "verfassungsrecht", "grundrechte",
    "verwaltungsrecht", "polizeirecht", "obg", "polg",
    "strafrecht", "stgb", "stpo",
    "zivilrecht", "bgb", "schadensersatz", "anfechtung",
    "arbeitsrecht", "europarecht",
    "staatsexamen", "jurastudium", "referendariat",
    "prüfungsrecht", "examensrelevant",
    # NRW-spezifisch
    "nrw", "nordrhein-westfalen", "münster", "düsseldorf",
    "hamm", "köln", "olg hamm", "olg düsseldorf",
])


def clean_html(text: str) -> str:
    """Entfernt HTML-Tags aus einem String."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def _parse_date(entry: dict) -> dt.datetime | None:
    """Parsed das Datum aus einem feedparser-Entry.

    Gibt immer ein timezone-aware datetime zurück (UTC) oder None.
    """
    from email.utils import parsedate_to_datetime

    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return None
    try:
        d = parsedate_to_datetime(raw)
        # Falls naive datetime zurückgegeben wird, UTC anhängen
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d
    except Exception:
        return None


@st.cache_data(ttl=1800, show_spinner=False)  # 30 Minuten cachen
def fetch_lto_feed(feed_url: str, limit: int = 10) -> list[dict]:
    """Lädt einen einzelnen LTO-RSS-Feed.

    Bei Netzwerkproblemen oder Parse-Fehlern wird eine leere Liste
    zurückgegeben (kein Crash der App).
    """
    try:
        feed = feedparser.parse(feed_url)
        # feedparser gibt bei Fehler bozo=True
        if feed.get("bozo") and not feed.get("entries"):
            return []
    except Exception:
        return []

    items = []
    for entry in feed.entries[:limit]:
        items.append(
            {
                "title": clean_html(entry.get("title", "")),
                "summary": clean_html(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "published": _parse_date(entry),
                "source": "Legal Tribune Online",
            }
        )
    return items


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_lto_news(
    selected_feeds: tuple[str, ...],  # tuple statt list wegen Caching (hashable)
    limit_per_feed: int = 8,
) -> list[dict]:
    """Lädt alle ausgewählten Feeds und sortiert nach Datum (neuste zuerst).

    Nimmt `tuple` statt `list` als Argument, weil st.cache_data
    nur hashbare Parameter cached.
    """
    # UTC-aware Fallback für Einträge ohne Datum
    _utc_min = dt.datetime.min.replace(tzinfo=dt.timezone.utc)

    all_items = []
    for feed_name in selected_feeds:
        feed_url = LTO_FEEDS.get(feed_name)
        if not feed_url:
            continue
        for item in fetch_lto_feed(feed_url, limit=limit_per_feed):
            item["category"] = feed_name
            all_items.append(item)

    return sorted(
        all_items,
        key=lambda x: x["published"] or _utc_min,
        reverse=True,
    )


def is_exam_relevant(item: dict) -> bool:
    """True, wenn Titel oder Zusammenfassung examensrelevante Keywords enthalten."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    return any(kw in text for kw in EXAM_KEYWORDS)
