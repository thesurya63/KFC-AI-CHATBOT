"""Verify the Chroma collection with sample queries."""
import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings

CHROMA_DIR = settings.CHROMA_PATH
EMBED_MODEL = settings.EMBEDDING_MODEL
COLLECTION_NAME = "kfc_documents"


def main() -> None:
    """Run verification queries against the Chroma collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = embedding_functions.OllamaEmbeddingFunction(
        url=f"{settings.OLLAMA_BASE_URL}/api/embeddings",
        model_name=EMBED_MODEL,
    )
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

    # Count documents
    count = collection.count()
    print(f"Collection '{COLLECTION_NAME}' has {count} documents\n")

    # Sample queries
    queries = [
        "What burgers does KFC have?",
        "How many calories in Hot Wings?",
        "Is there a free delivery offer?",
    ]
    for q in queries:
        results = collection.query(query_texts=[q], n_results=2)
        print(f"Q: {q}")
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            print(f"  [{meta['record_type']}] {doc[:80]}... (dist={dist:.3f})")
        print()


if __name__ == "__main__":
    main()