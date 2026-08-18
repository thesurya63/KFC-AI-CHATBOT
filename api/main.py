"""FastAPI application for the KFC RAG chatbot."""
import json
import logging
import sqlite3
import urllib.request

import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.graph import run_agent
from config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "kfc_documents"


app = FastAPI(title="KFC RAG Chatbot", version="1.1.0")

# Restricted CORS — origins come from settings (JSON list in .env).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    intent: str
    route: str
    grounded: bool


def _ollama_models() -> list[str]:
    """Return the model names currently available on the Ollama server."""
    try:
        with urllib.request.urlopen(
            f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [model["name"] for model in payload.get("models", [])]
    except Exception:
        return []


def _check_sqlite() -> dict:
    """Return a readiness report for the SQLite database."""
    try:
        conn = sqlite3.connect(settings.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        required = {"menu_items", "nutrition", "offers", "synthetic_orders"}
        counts = {}
        for table in sorted(tables & required):
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        ok = required.issubset(tables) and all(counts.values())
        return {
            "ok": bool(ok),
            "tables": sorted(tables),
            "counts": counts,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _check_chroma() -> dict:
    """Return a readiness report for the Chroma collection."""
    try:
        client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        types = {}
        if count:
            metadatas = collection.get()["metadatas"]
            for meta in metadatas:
                record_type = meta.get("record_type", "unknown")
                types[record_type] = types.get(record_type, 0) + 1
        return {
            "ok": count > 0 and types.get("legal", 0) > 0,
            "document_count": count,
            "record_types": types,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.get("/health")
def health() -> dict:
    """Service health check."""
    return {"status": "ok", "chat_model": settings.CHAT_MODEL}


@app.get("/readiness")
def readiness() -> dict:
    """Report readiness of SQLite, Chroma, and Ollama dependencies."""
    sqlite_report = _check_sqlite()
    chroma_report = _check_chroma()
    models = _ollama_models()
    required_models = [settings.CHAT_MODEL, settings.EMBEDDING_MODEL]
    available_models = [m for m in required_models if m in models]
    ollama_report = {
        "ok": len(available_models) == len(required_models),
        "available_models": available_models,
        "missing_models": [m for m in required_models if m not in models],
    }
    ready = (
        sqlite_report["ok"]
        and chroma_report["ok"]
        and ollama_report["ok"]
    )
    return {
        "ready": ready,
        "sqlite": sqlite_report,
        "chroma": chroma_report,
        "ollama": ollama_report,
    }


@app.get("/")
def index() -> FileResponse:
    """Serve the chat web UI."""
    return FileResponse("api/static/index.html")


@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    """Run the agent and return a grounded response."""
    try:
        result = run_agent(req.message)
        # Use .value to serialize the Intent enum as a plain string
        # e.g. Intent.MENU_SEARCH -> "menu_search" not "Intent.menu_search"
        intent_str = result["intent"].value if result.get("intent") else "unsupported"
        return ChatResponse(
            answer=result["answer"],
            intent=intent_str,
            route=result["route"] or "",
            grounded=result["grounded"],
        )
    except Exception:
        logger.exception("Agent failed for query: %s", req.message)
        raise HTTPException(
            status_code=500,
            detail="The assistant encountered an error. Please check the server logs.",
        )