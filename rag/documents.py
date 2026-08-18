"""Build Chroma-ready documents from RAG and legal source files."""
import re
from pathlib import Path

import pandas as pd

LEGAL_SOURCE_URL = "https://online.kfc.co.in/offers"
LEGAL_CAPTURED_AT = "2026-08-12"


def parse_rag_documents(df: pd.DataFrame) -> list[dict]:
    """Parse the row-per-document RAG_Documents sheet into document dicts.

    Each row stores one document across columns: the first column holds
    ``document_id: <id>``, the second ``text: <body>``, and the remaining
    columns hold ``metadata key: value`` pairs.
    """
    docs = []
    for _, row in df.iterrows():
        cells = [
            str(v).strip() for v in row.tolist() if pd.notna(v) and str(v).strip()
        ]
        if not cells:
            continue
        doc_id = (
            cells[0].split(":", 1)[1].strip() if "document_id" in cells[0] else ""
        )
        text = ""
        if len(cells) > 1:
            body = cells[1]
            text = body.split(":", 1)[1].strip() if body.lower().startswith("text") else body
        metadata = {}
        for cell in cells[2:]:
            if ":" in cell:
                key, _, value = cell.partition(":")
                metadata[key.strip()] = value.strip().rstrip("}")
        if doc_id and text:
            docs.append({"id": doc_id, "text": text, "metadata": metadata})
    return docs


def build_legal_docs(legal_md: Path) -> list[dict]:
    """Split the legal footer capture markdown into one document per section."""
    content = legal_md.read_text(encoding="utf-8")
    parts = re.split(r"^###\s+", content, flags=re.MULTILINE)
    docs = []
    for part in parts:
        lines = [ln for ln in part.splitlines() if ln.strip()]
        if not lines:
            continue
        section_name = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        doc_id = (
            "legal-" + re.sub(r"[^a-z0-9]+", "-", section_name.lower()).strip("-")
        )
        docs.append(
            {
                "id": doc_id,
                "text": f"KFC India legal and policy: {section_name}.\n{body}",
                "metadata": {
                    "record_type": "legal",
                    "page_title": "KFC India Legal and Footer Capture",
                    "source_url": LEGAL_SOURCE_URL,
                    "captured_at": LEGAL_CAPTURED_AT,
                    "document_type": "legal",
                    "section_name": section_name,
                    "verification_status": "captured",
                },
            }
        )
    return docs