"""Configuration consistency and centralization tests."""
from config import CODE_ROOT, settings

CHAT_MODEL = "gemma3:4b"
EMBED_MODEL = "qwen3-embedding:0.6b"


def test_paths_resolve_absolute():
    assert settings.SQLITE_PATH.is_absolute()
    assert settings.CHROMA_PATH.is_absolute()
    assert settings.DATA_ROOT.is_absolute()


def test_generated_data_exists():
    assert settings.SQLITE_PATH.exists()
    assert settings.CHROMA_PATH.exists()


def test_runtime_models_are_canonical():
    assert settings.CHAT_MODEL == CHAT_MODEL
    assert settings.EMBEDDING_MODEL == EMBED_MODEL


def test_env_example_matches_runtime_models():
    env = (CODE_ROOT / ".env.example").read_text(encoding="utf-8")
    assert f"CHAT_MODEL={CHAT_MODEL}" in env
    assert f"EMBEDDING_MODEL={EMBED_MODEL}" in env


def test_ollama_base_url_default():
    assert settings.OLLAMA_BASE_URL.startswith("http")


def test_cors_is_restricted():
    assert settings.CORS_ORIGINS
    assert "*" not in settings.CORS_ORIGINS


def test_relative_paths_resolve_against_code_root():
    assert settings.SQLITE_PATH == CODE_ROOT / "sqlite_db" / "kfc_chatbot.db"
    assert settings.CHROMA_PATH == CODE_ROOT / "chroma_db"