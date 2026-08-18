"""SQLite database integrity and content tests."""
import sqlite3

import pytest

from config import settings

DB = settings.SQLITE_PATH

pytestmark = pytest.mark.skipif(
    not DB.exists(),
    reason="SQLite database not built yet; run database/create_db.py and database/load_data.py",
)


def _conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def test_counts_populated():
    with _conn() as conn:
        assert conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM nutrition").fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM synthetic_orders").fetchone()[0] == 500


def test_no_duplicate_ids():
    with _conn() as conn:
        dupes = (
            "SELECT COUNT(*) - COUNT(DISTINCT product_id) FROM menu_items"
        )
        assert conn.execute(dupes).fetchone()[0] == 0
        assert (
            conn.execute(
                "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM synthetic_orders"
            ).fetchone()[0]
            == 0
        )


def test_required_fields_not_null():
    with _conn() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM menu_items WHERE product_name IS NULL"
        ).fetchone()[0] == 0


def test_legal_and_rag_tables_loaded():
    with _conn() as conn:
        assert conn.execute("SELECT COUNT(*) FROM legal_docs").fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM rag_documents").fetchone()[0] > 0


def test_offer_start_dates_unpublished():
    with _conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
        missing = conn.execute(
            "SELECT COUNT(*) FROM offers WHERE valid_from IS NULL"
        ).fetchone()[0]
        # Documents the known quality issue the responder must disclose.
        assert total > 0
        assert missing == total


def test_integrity_check_ok():
    with _conn() as conn:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"