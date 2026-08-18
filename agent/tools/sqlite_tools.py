"""SQLite lookup tools for the KFC chatbot agent."""
import sqlite3

from config import settings

DB_PATH = settings.SQLITE_PATH


def _connect() -> sqlite3.Connection:
    """Open a connection to the KFC database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def lookup_menu_by_id(product_id: str) -> dict | None:
    """Return a menu item by exact product_id."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM menu_items WHERE product_id = ?", (product_id,)
        ).fetchone()
    return dict(row) if row else None


def search_menu_by_name(query: str) -> list[dict]:
    """Search menu items by partial product name match."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM menu_items WHERE product_name LIKE ? LIMIT 5",
            (f"%{query}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def lookup_nutrition(product_name: str) -> dict | None:
    """Look up nutrition by exact product name."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM nutrition WHERE product_name = ?", (product_name,)
        ).fetchone()
    return dict(row) if row else None


def search_nutrition_by_key(product_key: str) -> list[dict]:
    """Search nutrition records by product key."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM nutrition WHERE product_key LIKE ?",
            (f"%{product_key}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def lookup_offer(offer_id: str) -> dict | None:
    """Look up an offer by exact offer_id."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM offers WHERE offer_id = ?", (offer_id,)
        ).fetchone()
    return dict(row) if row else None


def list_active_offers() -> list[dict]:
    """List offers that are currently valid (end date is today or in the future)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM offers WHERE valid_to IS NOT NULL AND valid_to >= DATE('now')"
        ).fetchall()
    return [dict(r) for r in rows]


def search_nutrition_by_allergen(allergen_term: str) -> list[dict]:
    """Search nutrition records where the allergens column contains the term."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM nutrition WHERE allergens LIKE ?",
            (f"%{allergen_term}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def lookup_order(order_id: str) -> dict | None:
    """Look up a synthetic order by exact order_id."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM synthetic_orders WHERE order_id = ?", (order_id,)
        ).fetchone()
    return dict(row) if row else None