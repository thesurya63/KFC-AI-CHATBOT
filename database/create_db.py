"""Create the KFC chatbot SQLite database from the schema file."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings

SCHEMA_PATH = settings.SQLITE_PATH.parent / "schema.sql"
DB_PATH = settings.SQLITE_PATH


def main():
    """Execute the schema SQL to create all tables."""
    conn = sqlite3.connect(DB_PATH)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()

    # Verify tables were created
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"Database created: {DB_PATH}")
    print(f"Tables: {', '.join(tables)}")


if __name__ == "__main__":
    main()