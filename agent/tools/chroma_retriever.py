"""Chroma retriever for the KFC chatbot agent."""
import chromadb
from chromadb.utils import embedding_functions

from config import settings

COLLECTION_NAME = "kfc_documents"

# Module-level singletons — created once on import, reused on every query.
# This avoids re-opening the Chroma DB file on every call, which risks
# Windows file locking errors and is unnecessarily slow.
_client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
_ef = embedding_functions.OllamaEmbeddingFunction(
    url=f"{settings.OLLAMA_BASE_URL}/api/embeddings",
    model_name=settings.EMBEDDING_MODEL,
)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME, embedding_function=_ef
)


def search_menu(query: str, n_results: int = 3) -> list[dict]:
    """Retrieve menu documents from Chroma filtered by record_type."""
    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"record_type": "menu"},
    )
    return _format_results(results)


def search_all(query: str, n_results: int = 4) -> list[dict]:
    """Search across all document types in the Chroma collection."""
    results = _collection.query(query_texts=[query], n_results=n_results)
    return _format_results(results)


def _format_results(results: dict) -> list[dict]:
    """Flatten Chroma query results into a usable list of dicts."""
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    return [
        {"text": d, "metadata": m, "distance": s}
        for d, m, s in zip(docs, metas, dists)
    ]