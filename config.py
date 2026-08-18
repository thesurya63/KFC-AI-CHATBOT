"""Central runtime configuration for the KFC chatbot.

Every model name, path, host, and port is defined here so runtime code,
data scripts, and the API read from one settings object. Values can be
overridden through environment variables or a `.env` file (see
`.env.example`). All relative paths resolve against the code root so the
project can run from any working directory.
"""
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CODE_ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Runtime settings for the KFC RAG chatbot."""

    model_config = SettingsConfigDict(
        env_file=CODE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATA_ROOT: Path = CODE_ROOT / "data_split"
    CHROMA_PATH: Path = CODE_ROOT / "chroma_db"
    SQLITE_PATH: Path = CODE_ROOT / "sqlite_db" / "kfc_chatbot.db"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CHAT_MODEL: str = "gemma3:4b"
    EMBEDDING_MODEL: str = "qwen3-embedding:0.6b"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("DATA_ROOT", "CHROMA_PATH", "SQLITE_PATH", mode="before")
    @classmethod
    def resolve_relative_paths(cls, value):
        path = Path(value)
        return path if path.is_absolute() else (CODE_ROOT / path)


settings = Settings()