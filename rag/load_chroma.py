"""Load KFC documents into Chroma DB using qwen3-embedding via Ollama."""
import sys
from pathlib import Path

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings
from rag.documents import build_legal_docs, parse_rag_documents

DATA_DIR = settings.DATA_ROOT / "CHROMA_EMBEDDINGS"
CHROMA_DIR = settings.CHROMA_PATH
EMBED_MODEL = settings.EMBEDDING_MODEL
COLLECTION_NAME = "kfc_documents"
BATCH_SIZE = 10  # Embed in small batches to avoid Ollama timeouts


def build_menu_docs(df: pd.DataFrame) -> list[dict]:
    """Convert menu rows into text documents with metadata."""
    docs = []
    for _, row in df.iterrows():
        text = (
            f"KFC menu item: {row['product_name']}. "
            f"Category: {row['category']}. "
            f"Description: {row['description']}. "
            f"Vegetarian: {row['vegetarian_status']}. "
            f"Calories: {row['calories']} kcal. "
            f"Allergens: {row['allergens']}."
        )
        docs.append({
            "id": row["product_id"],
            "text": text,
            "metadata": {
                "record_type": "menu",
                "product_name": row["product_name"],
                "category": row["category"],
                "source_file": "01_Menu_Master.xlsx",
            },
        })
    return docs


def build_nutrition_docs(df: pd.DataFrame) -> list[dict]:
    """Convert nutrition rows into text documents with metadata."""
    docs = []
    for _, row in df.iterrows():
        text = (
            f"KFC nutrition: {row['product_name']}. "
            f"Energy: {row['energy_kcal']} kcal. "
            f"Protein: {row['protein_g']}g. "
            f"Carbs: {row['carbohydrate_g']}g. "
            f"Total fat: {row['total_fat_g']}g. "
            f"Allergens: {row['allergens']}."
        )
        docs.append({
            "id": row["record_id"],
            "text": text,
            "metadata": {
                "record_type": "nutrition",
                "product_name": row["product_name"],
                "source_file": "02_Nutrition_Master.xlsx",
            },
        })
    return docs


def build_offer_docs(df: pd.DataFrame) -> list[dict]:
    """Convert offer rows into text documents with metadata."""
    docs = []
    for _, row in df.iterrows():
        text = (
            f"KFC offer: {row['offer_name']}. "
            f"Description: {row['description']}. "
            f"Minimum order: {row['minimum_order_value']}. "
            f"Terms: {row['terms']}."
        )
        docs.append({
            "id": row["offer_id"],
            "text": text,
            "metadata": {
                "record_type": "offer",
                "offer_name": row["offer_name"],
                "source_file": "03_Offers_Legal_Master.xlsx",
            },
        })
    return docs


def embed_in_batches(ef, texts: list[str]) -> list[list[float]]:
    """Embed texts in small batches to avoid Ollama timeouts."""
    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        result = ef(batch)
        embeddings.extend(result)
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")
    return embeddings


def main() -> None:
    """Load all documents into Chroma (clean rebuild)."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = embedding_functions.OllamaEmbeddingFunction(
        url=f"{settings.OLLAMA_BASE_URL}/api/embeddings",
        model_name=EMBED_MODEL,
    )
    # Start from a clean collection so stale or previously failed
    # rebuilds cannot leave orphaned documents behind.
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}' for clean rebuild")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=ef
    )

    all_docs = []
    # Menu
    menu = pd.read_excel(DATA_DIR / "01_Menu_Master.xlsx", sheet_name="Menu")
    all_docs.extend(build_menu_docs(menu))
    # Nutrition
    nutrition = pd.read_excel(DATA_DIR / "02_Nutrition_Master.xlsx", sheet_name="Nutrition")
    all_docs.extend(build_nutrition_docs(nutrition))
    # Offers
    offers = pd.read_excel(DATA_DIR / "03_Offers_Legal_Master.xlsx", sheet_name="Offers")
    all_docs.extend(build_offer_docs(offers))
    # RAG documents (row-per-document layout)
    rag = pd.read_excel(DATA_DIR / "05_RAG_QA_Master.xlsx", sheet_name="RAG_Documents")
    rag_docs = parse_rag_documents(rag)
    for doc in rag_docs:
        # Keep CSV-era artifacts under their own type and ID prefix so they
        # do not collide with the canonical xlsx-based menu/nutrition records.
        doc["metadata"]["record_type"] = "rag"
        doc["id"] = f"rag-{doc['id']}"
    print(f"RAG_Documents sheet parsed: {len(rag_docs)} documents")
    all_docs.extend(rag_docs)
    # Legal documents (record_type=legal)
    legal_md = DATA_DIR / "kfc_legal_footer_capture_2026-08-12.md"
    if legal_md.exists():
        legal_docs = build_legal_docs(legal_md)
        print(f"Legal capture parsed: {len(legal_docs)} documents")
        all_docs.extend(legal_docs)
    else:
        print(f"WARNING: {legal_md.name} not found; legal documents skipped")

    ids = [d["id"] for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]

    print(f"Embedding {len(all_docs)} documents in batches of {BATCH_SIZE}...")
    embeddings = embed_in_batches(ef, texts)

    collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    print(f"Loaded {len(all_docs)} documents into Chroma collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()