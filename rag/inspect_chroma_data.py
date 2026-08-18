"""Inspect CHROMA_EMBEDDINGS source files to understand document structure."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings

DATA_DIR = settings.DATA_ROOT / "CHROMA_EMBEDDINGS"


def inspect_excel(path: Path) -> None:
    """Print sheet names, row counts, and columns for an Excel file."""
    print(f"\n{'='*60}")
    print(f"FILE: {path.name}")
    xl = pd.ExcelFile(path)
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        print(f"\n  SHEET: {sheet} | ROWS: {len(df)} | COLS: {len(df.columns)}")
        print(f"  COLUMNS: {list(df.columns)[:8]}")
        if len(df) > 0:
            print(f"  FIRST ROW: {df.iloc[0].to_dict()}")


def main() -> None:
    """Inspect all Excel files in the CHROMA_EMBEDDINGS lane."""
    for f in sorted(DATA_DIR.glob("*.xlsx")):
        inspect_excel(f)


if __name__ == "__main__":
    main()