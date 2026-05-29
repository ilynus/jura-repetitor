"""Web-Fetcher mit Whitelist und Zweitquellen-Verifikation.

Nur die in `VERIFIED_SOURCES` gelisteten Domains werden abgerufen.
Bei kritischen Aussagen kann eine zweite Quelle zum Abgleich
verwendet werden.
"""
from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.config import VERIFIED_SOURCES


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; JuraRepetitor/0.1; "
        "personal learning tool)"
    )
}


def is_verified(url: str) -> bool:
    """True, wenn die Domain in der Whitelist steht."""
    try:
        host = urlparse(url).netloc.lower()
        # Trailing :port abschneiden
        host = host.split(":")[0]
        # www. ignorieren
        if host.startswith("www."):
            host = host[4:]
        return any(host == d or host.endswith("." + d) for d in VERIFIED_SOURCES)
    except Exception:
        return False


def fetch_clean_text(url: str, max_chars: int = 20_000) -> tuple[str, str] | None:
    """Lädt eine verifizierte Seite und extrahiert Klartext.

    Returns (title, text) oder None bei Fehler/nicht verifizierter URL.
    """
    if not is_verified(url):
        return None

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Boilerplate raus
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    title = (soup.title.string.strip() if soup.title and soup.title.string else url)
    text = soup.get_text(separator="\n", strip=True)

    # Zu viele Leerzeilen entfernen
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    text = "\n".join(lines)

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... gekürzt ...]"

    return title, text


def cross_check_urls(primary: str, secondary: str) -> dict:
    """Holt zwei Quellen und gibt beide zurück, damit der LLM
    sie gegeneinander abgleichen kann.

    Im UI/Prompt verwenden als: "Quelle A sagt X, Quelle B sagt Y —
    stimmen sie überein? Falls nicht, was ist die wahrscheinlichste
    Erklärung?"
    """
    a = fetch_clean_text(primary)
    b = fetch_clean_text(secondary)
    return {
        "primary": {"url": primary, "data": a},
        "secondary": {"url": secondary, "data": b},
    }
