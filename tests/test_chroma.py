"""Chroma collection coverage tests (no Ollama required)."""
from collections import Counter

import chromadb
import pytest

from config import settings

COLLECTION = "kfc_documents"
EXPECTED_TYPES = {"menu", "nutrition", "offer", "legal", "rag"}


def collection_exists() -> bool:
    try:
        client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
        client.get_collection(name=COLLECTION)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not collection_exists(),
    reason="Chroma collection not built yet; run rag/load_chroma.py (requires Ollama)",
)


def _collection():
    client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
    return client.get_collection(name=COLLECTION)


def test_collection_exists_and_populated():
    assert _collection().count() > 0


def test_record_types_covered():
    collection = _collection()
    types = Counter(meta["record_type"] for meta in collection.get()["metadatas"])
    for expected in EXPECTED_TYPES:
        assert types[expected] > 0, f"missing record_type: {expected}"


def test_legal_documents_present():
    collection = _collection()
    legal = collection.get(where={"record_type": "legal"})["metadatas"]
    assert len(legal) > 0


def test_document_ids_unique():
    collection = _collection()
    ids = collection.get()["ids"]
    assert len(ids) == len(set(ids))