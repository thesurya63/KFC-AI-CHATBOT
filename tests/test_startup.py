"""Verify the project starts and resolves paths from a non-root directory."""
import os
import subprocess
import sys
import tempfile

import pytest

from config import CODE_ROOT, settings

pytestmark = pytest.mark.skipif(
    not settings.SQLITE_PATH.exists(),
    reason="SQLite database not built yet; run database/create_db.py and database/load_data.py",
)

CODE = (
    "from config import settings; "
    "from agent.tools.sqlite_tools import lookup_order; "
    "from agent import graph; "
    "from agent.state import Intent; "
    "s = {'intent': Intent.ORDER_STATUS, 'entities': {'order_id': 'KFC-ORDER-0001'}, "
    "     'evidence': [], 'limitations': []}; "
    "s = graph.lookup_order(s); s = graph.validate(s); "
    "print(settings.SQLITE_PATH.exists(), settings.CHROMA_PATH.exists(), "
    "      s['grounded'], bool(lookup_order('KFC-ORDER-0001')))"
)


def test_startup_from_other_directory():
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(CODE_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", CODE],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip().endswith("True True True True")