# KFC RAG CHATBOT CODEBASE

Local, educational KFC customer-support and menu chatbot. Grounded agentic RAG:
SQLite for exact records, Chroma for searchable documents, LangGraph for routing,
and Ollama for a local chat model and local embeddings.

## Repository layout

```
.
├── config.py              # central settings (models, paths, host, CORS)
├── agent/                 # LangGraph agent (state, router, evidence, responder)
│   └── tools/             #   sqlite + chroma lookup tools
├── api/                   # FastAPI app + static web UI
├── database/              # SQLite schema, loaders, verification
├── rag/                   # Chroma document building and ingestion
├── data_split/            # canonical source workbooks (SQLITE + CHROMA lanes)
├── sqlite_db/             # generated SQLite database + schema.sql
├── chroma_db/             # generated Chroma collection (gitignored)
├── tests/                 # pytest suite
├── prepare_package.py     # deployment packaging script
└── *.md / LICENSE / .github/workflows/ci.yml
```

Generated databases (`sqlite_db/*.db`, `chroma_db/`) are not committed to git;
they are rebuilt with the scripts below. Source workbooks under `data_split/`
**are** committed so a fresh clone can rebuild everything.

## Required Ollama models

Pull these before starting the API (names are canonical):

```bash
ollama pull gemma3:4b          # chat model
ollama pull qwen3-embedding:0.6b  # embedding model
```

Verify with `ollama list`. The server must be running on `http://localhost:11434`.

## Setup

```bash
cd kfc-rag-chatbot-code
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
copy .env.example .env            # Windows; adjust values if needed
```

All paths and models are centralized in `config.py` and can be overridden via
`.env` or environment variables. Relative paths resolve against the project
root, so the code runs from any working directory.

## Build the data foundation (optional rebuild)

```bash
python database/create_db.py      # create tables from sqlite_db/schema.sql
python database/load_data.py      # load Excel masters into SQLite
python database/verify_db.py      # verify counts and sample rows
python rag/load_chroma.py         # embed documents into Chroma (menu, nutrition, offer, rag, legal)
python rag/verify_chroma.py       # verify Chroma collection
```

## Run the API

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

- Chat UI: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- Readiness (SQLite + Chroma + Ollama + models): http://127.0.0.1:8000/readiness
- Chat API: `POST /chat` with JSON `{"message": "..."}`

CORS origins are restricted to the values in `CORS_ORIGINS` (see `.env`).
Change them for any other deployment.

## Tests

```bash
python -m pytest -q
```

Tests cover intent routing, evidence grounding, SQLite integrity, Chroma
coverage (including legal records), API health/readiness/validation, config
consistency, and startup from a non-root directory.

## Deploy

```bash
python prepare_package.py
```

This checkpoints and closes the SQLite database (removing `-wal`/`-shm`
files) and writes `kfc_chatbot_deploy.zip` containing the code, generated
data, and databases (caches, logs, and `.env` excluded). Extract the zip,
install requirements, and run uvicorn from the extracted folder.

## Notes

- Prices are demo/reference prices unless verified by a location-specific
  official source.
- Orders are synthetic; all responses are grounded in the available data.
- Offer start dates are not published in the source capture; the chatbot
  states this when applicable.
