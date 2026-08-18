"""Shared test helpers."""
import json
import urllib.request

import pytest

from config import settings


def ollama_available() -> bool:
    """Return True if Ollama is running with the required models."""
    try:
        with urllib.request.urlopen(
            f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        names = {model["name"] for model in data.get("models", [])}
        return {settings.CHAT_MODEL, settings.EMBEDDING_MODEL}.issubset(names)
    except Exception:
        return False


requires_ollama = pytest.mark.skipif(
    not ollama_available(),
    reason="Ollama or the required models are not available",
)