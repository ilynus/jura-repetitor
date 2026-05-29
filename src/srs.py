"""Spaced Repetition mit dem klassischen SM-2 Algorithmus.

SM-2 wurde von Piotr Wozniak für SuperMemo entworfen und wird
von Anki, Mnemosyne und vielen anderen Lern-Apps genutzt.

Für jede Karte tracken wir:
- `efactor`: Wie "leicht" die Karte ist (1.3 = schwer, 2.5 = Standard)
- `interval`: Tage bis zur nächsten Wiederholung
- `repetitions`: Wie oft erfolgreich in Folge erinnert
- `due`: ISO-Datum, wann sie wieder dran ist
"""
from __future__ import annotations

import datetime as dt
from typing import Any


# Bewertungsskala (wie der Nutzer die Karte beantwortet hat)
GRADE_AGAIN = 0   # gar nicht gewusst
GRADE_HARD = 3    # nur mit Mühe
GRADE_GOOD = 4    # gewusst, normal
GRADE_EASY = 5    # spielend


def new_card_state() -> dict[str, Any]:
    """Initialer State für eine neue Karteikarte."""
    return {
        "efactor": 2.5,
        "interval": 0,
        "repetitions": 0,
        "due": today_iso(),
        "history": [],
    }


def update(state: dict[str, Any], grade: int) -> dict[str, Any]:
    """Aktualisiert den SRS-State einer Karte basierend auf der Bewertung.

    Gibt einen neuen State zurück (mutiert den alten nicht).
    """
    s = dict(state)
    s.setdefault("efactor", 2.5)
    s.setdefault("interval", 0)
    s.setdefault("repetitions", 0)
    s.setdefault("history", [])

    if grade < 3:
        # Wieder von vorn
        s["repetitions"] = 0
        s["interval"] = 1
    else:
        if s["repetitions"] == 0:
            s["interval"] = 1
        elif s["repetitions"] == 1:
            s["interval"] = 6
        else:
            s["interval"] = round(s["interval"] * s["efactor"])
        s["repetitions"] += 1

    # E-Factor updaten (SM-2 Formel)
    new_ef = s["efactor"] + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    s["efactor"] = max(1.3, new_ef)

    # Fälligkeitsdatum setzen
    next_due = dt.date.today() + dt.timedelta(days=s["interval"])
    s["due"] = next_due.isoformat()

    # History trimmen (max 50 Einträge)
    s["history"] = (s["history"] + [{"date": today_iso(), "grade": grade}])[-50:]

    return s


def is_due(state: dict[str, Any]) -> bool:
    """True, wenn die Karte heute oder früher fällig ist."""
    due = state.get("due", today_iso())
    return due <= today_iso()


def today_iso() -> str:
    return dt.date.today().isoformat()


def stats(cards: list[dict]) -> dict[str, int]:
    """Aggregierte Statistik über alle Karten."""
    total = len(cards)
    due = sum(1 for c in cards if is_due(c.get("srs", new_card_state())))
    learned = sum(
        1 for c in cards
        if c.get("srs", {}).get("repetitions", 0) >= 3
    )
    return {"total": total, "due": due, "learned": learned}
