"""Load validated Excel data into the SQLite chatbot database."""
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings
from rag.documents import parse_rag_documents

DATA_DIR = settings.DATA_ROOT / "SQLITE_STRUCTURED"
DB_PATH = settings.SQLITE_PATH

# Map Excel file -> (sheet, target table, column mapping)
LOADERS = {
    "01_Menu_Master.xlsx": [
        ("Menu", "menu_items", None),
        ("Reference_Prices", "reference_prices", None),
    ],
    "02_Nutrition_Master.xlsx": [
        ("Nutrition", "nutrition", None),
    ],
    "03_Offers_Legal_Master.xlsx": [
        ("Offers", "offers", None),
    ],
    "04_Orders_Master.xlsx": [
        ("Synthetic_Orders", "synthetic_orders", None),
    ],
}


def clean_value(value):
    """Convert pandas NaN to None for SQLite."""
    if pd.isna(value):
        return None
    return value


def load_sheet(conn, df, table):
    """Insert a DataFrame into a table, keeping only columns that exist."""
    table_cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    cols = [c for c in df.columns if c in table_cols]
    placeholders = ", ".join(["?"] * len(cols))
    col_list = ", ".join(cols)
    sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"
    rows = [tuple(clean_value(v) for v in row) for row in df[cols].itertuples(index=False)]
    conn.executemany(sql, rows)
    return len(rows)


def load_legal_footer(conn, path):
    """Load the Legal_Footer sheet into the legal_docs table."""
    df = pd.read_excel(path, sheet_name="Legal_Footer")
    col = df.columns[0]
    rows = [
        (int(i), str(value))
        for i, value in enumerate(df[col])
        if pd.notna(value) and str(value).strip()
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO legal_docs (line_number, content) VALUES (?, ?)",
        rows,
    )
    return len(rows)


def load_rag_documents(conn, path):
    """Load the RAG_Documents sheet into the rag_documents table."""
    df = pd.read_excel(path, sheet_name="RAG_Documents")
    docs = parse_rag_documents(df)
    rows = [
        (doc["id"], doc["text"], json.dumps(doc["metadata"], ensure_ascii=False))
        for doc in docs
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO rag_documents (doc_id, doc_text, doc_meta) VALUES (?, ?, ?)",
        rows,
    )
    return len(rows)


def main():
    """Load all validated Excel sheets into the database."""
    conn = sqlite3.connect(DB_PATH)
    total = 0
    for filename, sheets in LOADERS.items():
        path = DATA_DIR / filename
        if not path.exists():
            print(f"SKIP: {filename} not found")
            continue
        for sheet_name, table, _ in sheets:
            df = pd.read_excel(path, sheet_name=sheet_name)
            count = load_sheet(conn, df, table)
            total += count
            print(f"LOADED: {table} <- {filename} [{sheet_name}] ({count} rows)")

    offers_path = DATA_DIR / "03_Offers_Legal_Master.xlsx"
    if offers_path.exists():
        legal_count = load_legal_footer(conn, offers_path)
        total += legal_count
        print(f"LOADED: legal_docs <- {offers_path.name} [Legal_Footer] ({legal_count} rows)")

    rag_path = DATA_DIR / "05_RAG_QA_Master.xlsx"
    if not rag_path.exists():
        # RAG QA workbook lives in the Chroma lane; fall back there.
        rag_path = settings.DATA_ROOT / "CHROMA_EMBEDDINGS" / "05_RAG_QA_Master.xlsx"
    if rag_path.exists():
        rag_count = load_rag_documents(conn, rag_path)
        total += rag_count
        print(f"LOADED: rag_documents <- {rag_path.name} [RAG_Documents] ({rag_count} rows)")

    conn.commit()
    conn.close()
    print(f"\nTOTAL ROWS LOADED: {total}")


if __name__ == "__main__":
    main()