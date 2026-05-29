"""GitHub als Datenbank.

Liest und schreibt JSON-Dateien in einem privaten GitHub-Repository.
Jeder Write erzeugt einen Commit, sodass die History deiner Daten
versioniert ist.

Hinweise:
- Wir cachen Reads aggressiv im Streamlit Session State, weil sonst
  jeder Rerun einen API-Call bedeuten würde.
- Concurrent Writes sind nicht sicher → bei Single-User okay,
  bei Multi-User später migrieren.
"""
from __future__ import annotations

import json
import time
from typing import Any

import streamlit as st
from github import Github, GithubException, UnknownObjectException
from github.Repository import Repository

from src.config import get_secret


# ---------------------------------------------------------------- #
#  Verbindung
# ---------------------------------------------------------------- #

@st.cache_resource(show_spinner=False)
def _get_repo() -> Repository:
    """Hält eine Verbindung zum Daten-Repo über die Session."""
    token = get_secret("GITHUB_TOKEN")
    repo_name = get_secret("GITHUB_DATA_REPO")
    gh = Github(token)
    try:
        return gh.get_repo(repo_name)
    except GithubException as e:
        st.error(
            f"❌ Konnte das Daten-Repo `{repo_name}` nicht öffnen. "
            f"Prüfe Token-Permissions (Contents: Read & write) und "
            f"den Repo-Namen.\n\n`{e}`"
        )
        st.stop()


def _branch() -> str:
    return get_secret("GITHUB_DATA_BRANCH", "main") or "main"


# ---------------------------------------------------------------- #
#  Low-Level Operationen
# ---------------------------------------------------------------- #

def read_json(path: str, default: Any = None) -> Any:
    """Liest eine JSON-Datei aus dem Daten-Repo.

    Gibt `default` zurück, wenn die Datei (noch) nicht existiert.
    Wirf KEINE Exception bei Not-Found — das ist ein normaler Zustand.
    """
    cache_key = f"_gh_cache::{path}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    repo = _get_repo()
    try:
        f = repo.get_contents(path, ref=_branch())
        data = json.loads(f.decoded_content.decode("utf-8"))
        st.session_state[cache_key] = data
        # SHA für spätere Updates merken (GitHub API braucht den)
        st.session_state[f"_gh_sha::{path}"] = f.sha
        return data
    except UnknownObjectException:
        return default
    except GithubException as e:
        st.warning(f"GitHub-Lesefehler ({path}): {e}")
        return default


def write_json(path: str, data: Any, commit_msg: str | None = None) -> bool:
    """Schreibt JSON ins Daten-Repo. Erzeugt einen Commit.

    Gibt True bei Erfolg zurück.
    """
    repo = _get_repo()
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    msg = commit_msg or f"update {path}"
    sha_key = f"_gh_sha::{path}"

    try:
        if sha_key in st.session_state:
            # Update existierende Datei
            repo.update_file(
                path=path,
                message=msg,
                content=content,
                sha=st.session_state[sha_key],
                branch=_branch(),
            )
        else:
            # Versuch: erst lesen, dann updaten, sonst neu erstellen
            try:
                f = repo.get_contents(path, ref=_branch())
                repo.update_file(
                    path=path, message=msg, content=content,
                    sha=f.sha, branch=_branch(),
                )
            except UnknownObjectException:
                repo.create_file(
                    path=path, message=msg, content=content, branch=_branch(),
                )

        # Cache invalidieren
        st.session_state[f"_gh_cache::{path}"] = data
        # SHA-Cache leeren, damit beim nächsten Read der neue SHA geholt wird
        st.session_state.pop(sha_key, None)
        return True

    except GithubException as e:
        st.error(f"GitHub-Schreibfehler ({path}): {e}")
        return False


def list_dir(path: str) -> list[str]:
    """Listet Dateipfade in einem Verzeichnis des Daten-Repos."""
    repo = _get_repo()
    try:
        contents = repo.get_contents(path, ref=_branch())
        if not isinstance(contents, list):
            contents = [contents]
        return [c.path for c in contents if c.type == "file"]
    except UnknownObjectException:
        return []
    except GithubException:
        return []


def invalidate_cache(path: str) -> None:
    """Forciert Neuladen einer Datei beim nächsten read_json()."""
    st.session_state.pop(f"_gh_cache::{path}", None)
    st.session_state.pop(f"_gh_sha::{path}", None)


# ---------------------------------------------------------------- #
#  High-Level Helpers
# ---------------------------------------------------------------- #

def append_to_list_file(path: str, item: Any, commit_msg: str | None = None) -> bool:
    """Lädt eine JSON-Liste, hängt ein Element an, schreibt zurück."""
    items = read_json(path, default=[]) or []
    if not isinstance(items, list):
        items = []
    items.append(item)
    return write_json(path, items, commit_msg=commit_msg)


def update_dict_file(path: str, updates: dict, commit_msg: str | None = None) -> bool:
    """Lädt ein JSON-Dict, merged Updates rein, schreibt zurück."""
    data = read_json(path, default={}) or {}
    if not isinstance(data, dict):
        data = {}
    data.update(updates)
    return write_json(path, data, commit_msg=commit_msg)


def now_iso() -> str:
    """ISO-Timestamp für Datei-Namen und Commit-Messages."""
    return time.strftime("%Y-%m-%dT%H-%M-%S")
