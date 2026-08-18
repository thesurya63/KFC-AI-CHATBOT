"""Prepare a deployment package for the KFC RAG chatbot.

Steps:
1. Checkpoint and close the SQLite database so no -wal/-shm files exist.
2. Remove the checkpointed -wal and -shm files.
3. Zip the code, generated data, and databases, excluding caches, logs,
   secrets, and WAL/SHM files.

Run from the project root:
    python prepare_package.py
"""
import sqlite3
import zipfile
from pathlib import Path

from config import settings

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "kfc_chatbot_deploy.zip"

INCLUDE = [
    "config.py",
    "agent",
    "api",
    "database",
    "rag",
    "data_split",
    "sqlite_db",
    "chroma_db",
    "tests",
    "requirements.txt",
    ".env.example",
    "README.md",
    "AGENTS.md",
]

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log"}
EXCLUDE_NAMES = {".env", "kfc_chatbot_deploy.zip"}


def checkpoint_database() -> None:
    """Checkpoint WAL and remove the sidecar files."""
    db_path = settings.SQLITE_PATH
    if not db_path.exists():
        print(f"SKIP checkpoint: {db_path} not found")
        return
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("PRAGMA journal_mode = DELETE")
    conn.commit()
    conn.close()
    for suffix in (".db-wal", ".db-shm"):
        sidecar = db_path.with_name(db_path.name + suffix)
        if sidecar.exists():
            sidecar.unlink()
    print(f"SQLite checkpointed and closed: {db_path}")
    print(f"Remaining sqlite files: {[p.name for p in db_path.parent.glob(db_path.stem + '*')]}")


def build_package() -> None:
    """Write the deployment zip."""
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in INCLUDE:
            src = ROOT / rel
            if src.is_file():
                zf.write(src, rel)
            elif src.is_dir():
                for file in sorted(src.rglob("*")):
                    if not file.is_file():
                        continue
                    if any(part in EXCLUDE_DIRS for part in file.parts):
                        continue
                    if file.suffix in EXCLUDE_SUFFIXES:
                        continue
                    if file.name in EXCLUDE_NAMES:
                        continue
                    zf.write(file, file.relative_to(ROOT))
    print(f"Package written: {OUTPUT}")


def main() -> None:
    checkpoint_database()
    build_package()


if __name__ == "__main__":
    main()