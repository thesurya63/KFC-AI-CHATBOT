"""Verify the loaded SQLite database with sample queries."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings

DB_PATH = settings.SQLITE_PATH


def query(conn, sql, label):
    """Run a query and print results."""
    rows = conn.execute(sql).fetchall()
    print(f"{label}: {len(rows)} rows")
    for row in rows[:3]:
        print(f"  {dict(row)}")
    print()


def main():
    """Run verification queries against the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("=== DATABASE VERIFICATION ===\n")

    query(conn, "SELECT COUNT(*) FROM menu_items", "Menu items")
    query(conn, "SELECT product_id, product_name, price_status FROM menu_items LIMIT 3", "Sample menu")

    query(conn, "SELECT COUNT(*) FROM reference_prices", "Reference prices")
    query(conn, "SELECT reference_product_name, reference_price_inr FROM reference_prices LIMIT 3", "Sample prices")

    query(conn, "SELECT COUNT(*) FROM nutrition", "Nutrition records")
    query(conn, "SELECT record_id, product_name FROM nutrition LIMIT 3", "Sample nutrition")

    query(conn, "SELECT COUNT(*) FROM offers", "Offers")
    query(conn, "SELECT offer_id, offer_name, valid_to FROM offers LIMIT 3", "Sample offers")

    query(conn, "SELECT COUNT(*) FROM synthetic_orders", "Orders")
    query(conn, "SELECT order_id, order_status FROM synthetic_orders LIMIT 3", "Sample orders")

    query(conn, "SELECT COUNT(*) FROM legal_docs", "Legal footer lines")
    query(conn, "SELECT COUNT(*) FROM rag_documents", "RAG documents")

    conn.close()
    print("=== VERIFICATION COMPLETE ===")


if __name__ == "__main__":
    main()