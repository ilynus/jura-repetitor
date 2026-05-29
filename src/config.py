"""Zentrale Konfiguration: Modelle, Whitelist, Pfad-System (shared/personal)."""
from __future__ import annotations

import streamlit as st


# --- Claude Modelle ---
MODEL_DEFAULT = "claude-sonnet-4-6"
MODEL_HEAVY = "claude-opus-4-7"
MODEL_FAST = "claude-haiku-4-5-20251001"

MAX_TOKENS_OUT = 4096
MAX_TOKENS_OUT_LONG = 8192


# --- Verifizierte juristische Quellen ---
VERIFIED_SOURCES = [
    # Bundes-Justiz
    "dejure.org",
    "gesetze-im-internet.de",
    "rechtsprechung-im-internet.de",
    "bverfg.de",
    "bundesgerichtshof.de",
    "openjur.de",
    "bundesverwaltungsgericht.de",
    "bundesarbeitsgericht.de",
    "bundesfinanzhof.de",
    "bundessozialgericht.de",
    # NRW-spezifisch
    "recht.nrw.de",
    "jm.nrw.de",
    "olg-hamm.nrw.de",
    "olg-duesseldorf.nrw.de",
    "olg-koeln.nrw.de",
    # Universität Münster
    "uni-muenster.de",
    "jura.uni-muenster.de",
    # Europäische Quellen
    "curia.europa.eu",
    "eur-lex.europa.eu",
    "echr.coe.int",
]


# ================================================================ #
#  PFAD-SYSTEM
# ================================================================ #
#
#  GitHub-Daten-Repo Struktur:
#
#  users/
#    _registry.json              ← Nutzerliste (auth.py)
#    shared/
#      materials_index.json      ← Gemeinsame Materialien
#      flashcards.json           ← Gemeinsame Karteikarten
#    {username}/
#      materials_index.json      ← Persönliche Materialien
#      flashcards.json
#      progress.json
#      corrections/
#        {ts}.json
#      learning_plans.json
#      chats/
#        {session_id}.json
#
# ================================================================ #

def _current_username() -> str:
    """Gibt den eingeloggten Nutzernamen zurück.
    Fällt auf 'default' zurück wenn noch kein Auth-System aktiv."""
    user = st.session_state.get("auth_user")
    if user:
        return user["username"]
    # Fallback: SECRET USER_ID (legacy / single-user Modus)
    try:
        return st.secrets.get("USER_ID", "default")
    except Exception:
        return "default"


def shared_path(*parts: str) -> str:
    """Pfad in der gemeinsamen Ablage: users/shared/{parts}"""
    return "/".join(["users", "shared", *parts])


def personal_path(*parts: str) -> str:
    """Pfad im persönlichen Bereich des aktuellen Nutzers: users/{username}/{parts}"""
    return "/".join(["users", _current_username(), *parts])


def user_path(*parts: str) -> str:
    """Legacy-Alias → persönlicher Pfad."""
    return personal_path(*parts)


# --- Gemeinsame Pfade ---
PATH_SHARED_MATERIALS = lambda: shared_path("materials_index.json")
PATH_SHARED_FLASHCARDS = lambda: shared_path("flashcards.json")

# --- Persönliche Pfade ---
PATH_MATERIALS = lambda: personal_path("materials_index.json")
PATH_FLASHCARDS = lambda: personal_path("flashcards.json")
PATH_PROGRESS = lambda: personal_path("progress.json")
PATH_CORRECTIONS = lambda ts: personal_path("corrections", f"{ts}.json")
PATH_CHAT_HISTORY = lambda session_id: personal_path("chats", f"{session_id}.json")
PATH_PLANS = lambda: personal_path("learning_plans.json")
PATH_PROFILE = lambda: personal_path("profile.json")
PATH_TODO = lambda: personal_path("todo.json")
PATH_FOCUS = lambda: personal_path("focus.json")
PATH_FEEDBACK = lambda: shared_path("feedback.json")  # shared → Admin sieht alle


# --- Quellentyp-Labels (für visuelle Markierung) ---
SOURCE_TYPE_SHARED = "shared"
SOURCE_TYPE_PERSONAL = "personal"

SOURCE_BADGE = {
    SOURCE_TYPE_SHARED: "🔵 Gemeinsam",
    SOURCE_TYPE_PERSONAL: "🟢 Persönlich",
}

SOURCE_COLOR = {
    SOURCE_TYPE_SHARED: "#dbeafe",    # Blau-100
    SOURCE_TYPE_PERSONAL: "#dcfce7",  # Grün-100
}

SOURCE_LLM_TAG = {
    SOURCE_TYPE_SHARED: "[GEMEINSAMES MATERIAL]",
    SOURCE_TYPE_PERSONAL: "[PERSÖNLICHES MATERIAL]",
}


# --- Limits ---
MAX_MATERIAL_CHARS = 200_000
MAX_UPLOAD_MB = 50


def get_secret(key: str, default: str | None = None) -> str | None:
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        if default is not None:
            return default
        st.error(
            f"⚠️ Secret `{key}` fehlt. "
            f"Trage es in `.streamlit/secrets.toml` ein."
        )
        st.stop()
