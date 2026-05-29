"""Text-Extraktion aus PDF, DOCX, TXT, MD.

Wichtig für den juristischen Zitierstandard: Bei PDFs werden Seitenzahlen
mit `[Seite N]`-Markierungen in den Text eingefügt, sodass Claude darauf
referenzieren kann ("Skript_AT, S. 47").
"""
from __future__ import annotations

import io
from typing import Any

from src.config import MAX_MATERIAL_CHARS


def extract_text(uploaded_file: Any) -> tuple[str, str, int]:
    """Extrahiert Text aus einem Streamlit-UploadedFile.

    Returns:
        (name, text_mit_seitenmarkierungen, seitenanzahl)
    """
    name = uploaded_file.name
    suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""

    if suffix == "pdf":
        text, pages = _from_pdf(uploaded_file)
    elif suffix == "docx":
        text = _from_docx(uploaded_file)
        pages = 1  # docx hat keine echten Seiten ohne Rendering
    elif suffix in ("txt", "md"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        pages = 1
    else:
        raise ValueError(
            f"Dateityp `.{suffix}` wird nicht unterstützt. "
            f"Erlaubt: PDF, DOCX, TXT, MD."
        )

    text = text.strip()
    if len(text) > MAX_MATERIAL_CHARS:
        text = text[:MAX_MATERIAL_CHARS] + "\n\n[... gekürzt, Material zu groß ...]"
    return name, text, pages


def _from_pdf(uploaded_file: Any) -> tuple[str, int]:
    """PDF mit klaren Seitenmarkierungen extrahieren."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    pages_out = []
    page_count = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        try:
            page_text = (page.extract_text() or "").strip()
        except Exception:
            page_text = "[Extraktion fehlgeschlagen]"
        if page_text:
            pages_out.append(f"[Seite {i}]\n{page_text}")

    return "\n\n".join(pages_out), page_count


def _from_docx(uploaded_file: Any) -> str:
    from docx import Document

    doc = Document(io.BytesIO(uploaded_file.read()))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
