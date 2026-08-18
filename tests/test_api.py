"""API health, readiness, and /chat validation tests."""
import pytest
from fastapi.testclient import TestClient

from api.main import app
from config import settings
from helpers import requires_ollama

client = TestClient(app)


def _dependencies_ready() -> bool:
    """True when the generated DB and Ollama models are available."""
    data_ready = settings.SQLITE_PATH.exists()
    try:
        import chromadb

        chromadb.PersistentClient(path=str(settings.CHROMA_PATH)).get_collection(
            name="kfc_documents"
        )
    except Exception:
        return False
    return data_ready


deps_ready = pytest.mark.skipif(
    not _dependencies_ready(),
    reason="Build the database (database/) and Chroma (rag/) first",
)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["chat_model"] == "gemma3:4b"


def test_readiness_shape():
    response = client.get("/readiness")
    assert response.status_code == 200
    for key in ("ready", "sqlite", "chroma", "ollama"):
        assert key in response.json()


@deps_ready
def test_readiness_dependencies_ok():
    data = client.get("/readiness").json()
    assert data["sqlite"]["ok"] is True
    assert data["chroma"]["ok"] is True
    assert data["ollama"]["ok"] is True
    assert data["ready"] is True


def test_chat_missing_message_422():
    assert client.post("/chat", json={}).status_code == 422


def test_chat_wrong_type_422():
    assert client.post("/chat", json={"message": 123}).status_code == 422


@requires_ollama
def test_chat_valid_request_200():
    response = client.post("/chat", json={"message": "What burgers does KFC have?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert "grounded" in data
    assert "intent" in data