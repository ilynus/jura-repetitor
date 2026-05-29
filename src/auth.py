"""Authentifizierung und Nutzerverwaltung.

Architektur:
- Nutzerdaten liegen als `users/_registry.json` im GitHub-Daten-Repo
- Passwörter werden mit bcrypt gehasht, niemals im Klartext gespeichert
- Sessions laufen über st.session_state (kein Cookie-Framework nötig)
- Rollen: "admin" (darf shared Materialien verwalten) und "user"

Pfade im GitHub-Repo:
  users/_registry.json        Nutzerliste
  users/shared/...            Gemeinsame Materialien
  users/{username}/...        Persönliche Daten

Nutzung in jeder Page:
  from src.auth import require_login
  user = require_login()   # gibt User-Dict zurück oder stoppt die Page
"""
from __future__ import annotations

import re
import time
from typing import Any

import bcrypt
import streamlit as st

from src.github_db import read_json, write_json

# Pfad der Nutzerliste im Daten-Repo
REGISTRY_PATH = "users/_registry.json"


# ---------------------------------------------------------------- #
#  Interne Helpers
# ---------------------------------------------------------------- #

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def _check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def _load_registry() -> dict[str, dict]:
    """Lädt die Nutzerliste. Format: {username: {email, pw_hash, role, created}}"""
    data = read_json(REGISTRY_PATH, default={}) or {}
    return data


def _save_registry(registry: dict[str, dict]) -> bool:
    return write_json(
        REGISTRY_PATH,
        registry,
        commit_msg="update user registry",
    )


def _validate_username(username: str) -> str | None:
    """Gibt eine Fehlermeldung zurück oder None wenn OK."""
    if len(username) < 3:
        return "Nutzername mind. 3 Zeichen."
    if len(username) > 30:
        return "Nutzername max. 30 Zeichen."
    if not re.match(r"^[a-z0-9_\-]+$", username):
        return "Nur Kleinbuchstaben, Ziffern, _ und - erlaubt."
    return None


def _validate_password(pw: str) -> str | None:
    if len(pw) < 8:
        return "Passwort mind. 8 Zeichen."
    return None


# ---------------------------------------------------------------- #
#  Öffentliche Auth-API
# ---------------------------------------------------------------- #

def get_current_user() -> dict | None:
    """Gibt den eingeloggten Nutzer aus dem Session State zurück."""
    return st.session_state.get("auth_user")


def is_admin() -> bool:
    u = get_current_user()
    return bool(u and u.get("role") == "admin")


def is_logged_in() -> bool:
    return get_current_user() is not None


def login(username: str, password: str) -> tuple[bool, str]:
    """Versucht Login. Gibt (success, message) zurück."""
    registry = _load_registry()
    entry = registry.get(username.lower())
    if not entry:
        return False, "Nutzername oder Passwort falsch."
    if not _check_password(password, entry.get("pw_hash", "")):
        return False, "Nutzername oder Passwort falsch."
    st.session_state["auth_user"] = {
        "username": username.lower(),
        "display_name": entry.get("display_name", username),
        "email": entry.get("email", ""),
        "role": entry.get("role", "user"),
    }
    return True, "Willkommen!"


def logout() -> None:
    st.session_state.pop("auth_user", None)
    st.rerun()


def register(
    username: str,
    password: str,
    email: str = "",
    display_name: str = "",
    role: str = "user",
) -> tuple[bool, str]:
    """Registriert einen neuen Nutzer. Gibt (success, message) zurück."""
    username = username.lower().strip()

    err = _validate_username(username)
    if err:
        return False, err
    err = _validate_password(password)
    if err:
        return False, err

    registry = _load_registry()
    if username in registry:
        return False, f"Nutzername '{username}' ist bereits vergeben."

    registry[username] = {
        "display_name": display_name.strip() or username,
        "email": email.strip(),
        "pw_hash": _hash_password(password),
        "role": role,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    ok = _save_registry(registry)
    if ok:
        return True, f"Account '{username}' wurde erstellt."
    return False, "Fehler beim Speichern. GitHub-Verbindung prüfen."


def list_users() -> list[dict]:
    """Gibt alle Nutzer zurück (ohne pw_hash). Nur für Admins."""
    reg = _load_registry()
    return [
        {k: v for k, v in entry.items() if k != "pw_hash"} | {"username": uname}
        for uname, entry in reg.items()
    ]


def change_password(username: str, old_pw: str, new_pw: str) -> tuple[bool, str]:
    registry = _load_registry()
    entry = registry.get(username)
    if not entry or not _check_password(old_pw, entry["pw_hash"]):
        return False, "Altes Passwort falsch."
    err = _validate_password(new_pw)
    if err:
        return False, err
    registry[username]["pw_hash"] = _hash_password(new_pw)
    ok = _save_registry(registry)
    return (True, "Passwort geändert.") if ok else (False, "Speicherfehler.")


def promote_to_admin(username: str) -> tuple[bool, str]:
    """Befördert einen Nutzer zum Admin. Nur von Admins aufrufbar."""
    registry = _load_registry()
    if username not in registry:
        return False, "Nutzer nicht gefunden."
    registry[username]["role"] = "admin"
    ok = _save_registry(registry)
    return (True, f"{username} ist jetzt Admin.") if ok else (False, "Speicherfehler.")


def bootstrap_admin_if_empty() -> None:
    """Wenn noch keine Nutzer existieren, wird ein Default-Admin aus
    secrets.toml angelegt (ADMIN_USER / ADMIN_PASSWORD).
    Verhindert, dass die App für neue Instanzen unzugänglich ist."""
    from src.config import get_secret

    registry = _load_registry()
    if registry:
        return  # Nutzer existieren bereits

    admin_user = get_secret("ADMIN_USER", default="admin")
    admin_pw = get_secret("ADMIN_PASSWORD", default=None)

    if not admin_pw:
        st.warning(
            "⚠️ Noch kein Nutzer angelegt und kein `ADMIN_PASSWORD` in "
            "`secrets.toml` gesetzt. Bitte ergänzen und App neu starten."
        )
        st.stop()

    ok, msg = register(
        admin_user, admin_pw,
        display_name="Admin",
        role="admin",
    )
    if ok:
        st.success(f"✅ Erster Admin-Account `{admin_user}` wurde erstellt.")


# ---------------------------------------------------------------- #
#  Page Guard — in jede Seite einbinden
# ---------------------------------------------------------------- #

def require_login(page_title: str = "") -> dict:
    """Stellt sicher, dass der Nutzer eingeloggt ist.

    Wenn nicht, wird die Login-UI angezeigt und st.stop() aufgerufen.
    Gibt bei Erfolg das User-Dict zurück.

    Verwendung am Seitenstart:
        user = require_login()
        # Ab hier: user["username"], user["display_name"], user["role"]
    """
    bootstrap_admin_if_empty()

    if is_logged_in():
        return get_current_user()

    # ---- Login-Formular ----
    st.title("🔐 Anmelden")
    if page_title:
        st.caption(f"Anmeldung erforderlich für: {page_title}")

    tab_login, tab_register = st.tabs(["Anmelden", "Registrieren"])

    with tab_login:
        with st.form("login_form"):
            uname = st.text_input("Nutzername")
            pw = st.text_input("Passwort", type="password")
            submitted = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
        if submitted:
            ok, msg = login(uname.strip(), pw)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        st.caption(
            "Neuen Account erstellen. Der erste Account wird automatisch Admin."
        )
        with st.form("register_form"):
            new_uname = st.text_input("Nutzername (nur a–z, 0–9, _, -)")
            new_display = st.text_input("Anzeigename (z.B. Max Mustermann)")
            new_email = st.text_input("E-Mail (optional)")
            new_pw = st.text_input("Passwort (mind. 8 Zeichen)", type="password")
            new_pw2 = st.text_input("Passwort wiederholen", type="password")
            reg_submitted = st.form_submit_button("Account erstellen", use_container_width=True)
        if reg_submitted:
            if new_pw != new_pw2:
                st.error("Passwörter stimmen nicht überein.")
            else:
                # Erster Nutzer wird Admin
                reg = _load_registry()
                role = "admin" if not reg else "user"
                ok, msg = register(new_uname, new_pw, new_email, new_display, role)
                if ok:
                    st.success(msg + " Bitte jetzt einloggen.")
                else:
                    st.error(msg)

    st.stop()
    return {}  # type: ignore  — wird nie erreicht
