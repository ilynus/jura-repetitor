"""Claude API Wrapper — Token-optimiert.

Optimierungen:
1. Cache-Reihenfolge FIXIERT:
   Block 1: System-Prompt (STATISCH → wird gecached ✓)
   Block 2: Profil (dynamisch, klein, NICHT gecached)
   Block 3: Materialien (dynamisch, NICHT gecached)
   Vorher war Profil Block 1 → hat Cache für System-Prompt gebrochen!

2. Modell-Routing:
   - Sonnet 4.6: Chat, Analyse, Korrektur
   - Opus 4.7: Nur Korrektor (explizit)
   - Haiku 4.5: JSON-Generierung (Karten, Fälle, Streitstände) → ~10x günstiger

3. History-Pruning: max. HISTORY_LIMIT Messages → verhindert unbegrenzten Anstieg

4. Material-Truncation: max. MAX_MATERIAL_CONTEXT Zeichen über alle Materialien
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import anthropic
import streamlit as st

from src.config import (
    MAX_TOKENS_OUT,
    MAX_TOKENS_OUT_LONG,
    MODEL_DEFAULT,
    MODEL_FAST,
    MODEL_HEAVY,
    get_secret,
)

# ── Limits ───────────────────────────────────────────────────
HISTORY_LIMIT = 12          # Max. Nachrichten in Chat-History
MAX_MATERIAL_CONTEXT = 60_000  # Max. Zeichen aller Materialien zusammen


@st.cache_resource(show_spinner=False)
def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_secret("ANTHROPIC_API_KEY"))


def _prune_history(messages: list[dict]) -> list[dict]:
    """Begrenzt Chat-History auf HISTORY_LIMIT Nachrichten.
    Behält immer die letzten N Nachrichten (paarweise user/assistant).
    """
    if len(messages) <= HISTORY_LIMIT:
        return messages
    # Immer pairs behalten: user+assistant
    pruned = messages[-HISTORY_LIMIT:]
    # Sicherstellen dass erstes Element user ist
    while pruned and pruned[0]["role"] == "assistant":
        pruned = pruned[1:]
    return pruned


def _truncate_materials(materials: list[dict]) -> list[dict]:
    """Kürzt Materialien proportional wenn Gesamtlimit überschritten."""
    if not materials:
        return []
    total = sum(len(m.get("text", "")) for m in materials)
    if total <= MAX_MATERIAL_CONTEXT:
        return materials
    ratio = MAX_MATERIAL_CONTEXT / total
    result = []
    for m in materials:
        entry = dict(m)
        text = m.get("text", "")
        limit = int(len(text) * ratio)
        if len(text) > limit:
            entry["text"] = text[:limit] + f"\n\n[... {len(text)-limit:,} Zeichen gekürzt]"
        result.append(entry)
    return result


def _build_system_blocks(
    system_prompt: str,
    materials: list[dict] | None = None,
    include_profile: bool = True,
) -> list[dict[str, Any]]:
    """Baut die System-Block-Liste für die Anthropic-API.

    REIHENFOLGE (wichtig für Prompt-Caching!):
      1. System-Prompt  ← STATISCH → cache_control → wird gecached
      2. Profil         ← dynamisch (pro User) → KEIN cache_control
      3. Materialien    ← dynamisch → KEIN cache_control

    Nur Block 1 ist über alle Requests identisch → nur er wird gecached.
    Profil und Materialien sind zu variabel für Cache.
    """
    blocks: list[dict[str, Any]] = []

    # ── 1. System-Prompt (gecached) ──────────────────────────
    blocks.append({
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"},  # ← gecached ✓
    })

    # ── 2. Nutzerprofil (NICHT gecached — ändert sich) ───────
    if include_profile:
        try:
            from src.profile import build_profile_context
            uname = st.session_state.get("auth_user", {}).get("username", "default")
            profile_ctx = build_profile_context(uname)
            if profile_ctx:
                blocks.append({
                    "type": "text",
                    "text": profile_ctx,
                    # KEIN cache_control — dynamisch
                })
        except Exception:
            pass

    # ── 3. Materialien (NICHT gecached — zu variabel) ─────────
    if materials:
        mats = _truncate_materials(materials)
        parts = [
            "\n\n---\n# Materialien des Nutzers\n\n"
            "Beziehe dich primär darauf. Zitiere mit `Dateiname, S. X`.\n\n"
        ]
        for m in mats:
            tag = m.get("topic", "")
            parts.append(f"## {m['name']}{' — ' + tag if tag else ''}\n\n{m['text']}\n\n")
        blocks.append({
            "type": "text",
            "text": "".join(parts),
            # KEIN cache_control
        })

    return blocks


# ── Öffentliche API ───────────────────────────────────────────

def chat_stream(
    messages: list[dict],
    system_prompt: str,
    materials: list[dict] | None = None,
    model: str = MODEL_DEFAULT,
    max_tokens: int = MAX_TOKENS_OUT,
) -> Iterator[str]:
    """Streamt Claude-Antworten. History wird automatisch geprüft."""
    pruned = _prune_history(messages)
    system_blocks = _build_system_blocks(system_prompt, materials)
    try:
        with _client().messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system_blocks,
            messages=pruned,
        ) as stream:
            for text in stream.text_stream:
                yield text
    except anthropic.APIError as e:
        yield f"\n\n⚠️ API-Fehler: `{e}`"


def chat_complete(
    messages: list[dict],
    system_prompt: str,
    materials: list[dict] | None = None,
    model: str = MODEL_DEFAULT,
    max_tokens: int = MAX_TOKENS_OUT,
) -> str:
    """Nicht-streamend. Für Analyse, Einordnung, Planung."""
    pruned = _prune_history(messages)
    system_blocks = _build_system_blocks(system_prompt, materials)
    try:
        resp = _client().messages.create(
            model=model, max_tokens=max_tokens,
            system=system_blocks, messages=pruned,
        )
        return resp.content[0].text if resp.content else ""
    except anthropic.APIError as e:
        return f"⚠️ API-Fehler: `{e}`"


def json_complete(
    user_prompt: str,
    system_prompt: str,
    max_tokens: int = 2048,
) -> str:
    """JSON-Generierung mit Haiku (~10x günstiger als Sonnet).
    
    Verwendet für: Karteikarten, Fälle, Streitstände, Quellenmatrix.
    Kein Profil-Kontext nötig (JSON-Ausgabe, keine personalisierte Erklärung).
    History nicht relevant (single-turn).
    """
    try:
        resp = _client().messages.create(
            model=MODEL_FAST,   # ← Haiku statt Sonnet
            max_tokens=max_tokens,
            system=[{"type": "text", "text": system_prompt}],
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text if resp.content else ""
    except anthropic.APIError as e:
        return f"⚠️ API-Fehler: `{e}`"


def heavy_complete(
    messages: list[dict],
    system_prompt: str,
    materials: list[dict] | None = None,
) -> str:
    """Opus 4.7 — nur für Klausur-Korrektur (höchste Qualität nötig)."""
    return chat_complete(
        messages, system_prompt, materials=materials,
        model=MODEL_HEAVY, max_tokens=MAX_TOKENS_OUT_LONG,
    )


def vision_complete(
    image_b64: str, media_type: str,
    user_prompt: str, system_prompt: str,
    model: str = MODEL_DEFAULT,
    max_tokens: int = MAX_TOKENS_OUT_LONG,
) -> str:
    """Vision-API für Handschrift-OCR."""
    system_blocks = _build_system_blocks(system_prompt, include_profile=False)
    messages = [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
        {"type": "text", "text": user_prompt},
    ]}]
    try:
        resp = _client().messages.create(
            model=model, max_tokens=max_tokens,
            system=system_blocks, messages=messages,
        )
        return resp.content[0].text if resp.content else ""
    except Exception as e:
        return f"⚠️ Vision-Fehler: `{e}`"


def vision_stream(
    image_b64: str, media_type: str,
    user_prompt: str, system_prompt: str,
    model: str = MODEL_DEFAULT,
    max_tokens: int = MAX_TOKENS_OUT_LONG,
) -> Iterator[str]:
    """Vision-API streaming."""
    system_blocks = _build_system_blocks(system_prompt, include_profile=False)
    messages = [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
        {"type": "text", "text": user_prompt},
    ]}]
    try:
        with _client().messages.stream(
            model=model, max_tokens=max_tokens,
            system=system_blocks, messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        yield f"\n\n⚠️ Vision-Fehler: `{e}`"
