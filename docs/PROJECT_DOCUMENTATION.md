# KFC AI CHATBOT — Project Documentation

A local, educational KFC customer-support and menu chatbot built as a grounded
agentic RAG (Retrieval-Augmented Generation) system. This document explains
the project end to end: what it does, how it is structured, how the data
flows, and how to run it.

> **Scope note:** This is a local educational demonstration, not a real KFC
> production system. Orders are synthetic. Prices are demo/reference prices
> unless verified for a specific location. The chatbot only answers from
> retrieved knowledge-base records or SQLite query results and never invents
> facts.

---

## 1. What the chatbot does

A customer can ask:

- **Menu search** — find KFC products by name, category, description, and
  demo price.
- **Nutrition & allergens** — energy, protein, carbs, fat, sugar, and
  allergen statements per product.
- **Offers** — current demo offers, terms, channels, and validity. When a
  start or end date is not published, the assistant says so explicitly.
- **Order status** — synthetic order lookups by order ID (`KFC-ORDER-####`):
  delivery status, delay reasons, missing items, and refund status.
- **Legal / policy** — terms and conditions, disclaimer, and caution notice
  summaries grounded in the captured legal reference documents.
- **Recommendations** — product suggestions grounded in the available data.

Anything outside these topics receives a safe, non-hallucinated refusal.

---

## 2. System architecture

```
User query
   │
   ▼
[normalize]  ── classify intent + extract entities (deterministic rules)
   │
   ├─ MENU_SEARCH / MENU_DETAIL ──► [search_menu]     Chroma (record_type=menu)
   ├─ NUTRITION / ALLERGEN      ──► [lookup_nutrition] SQLite (nutrition table)
   ├─ OFFER                     ──► [lookup_offer]    SQLite (offers table)
   ├─ ORDER_STATUS / DELIVERY   ──► [lookup_order]    SQLite (synthetic_orders)
   ├─ LEGAL_POLICY              ──► [search_legal]    Chroma (record_type=legal)
   ├─ RECOMMENDATION            ──► [recommend]       Chroma + SQLite (hybrid)
   └─ UNSUPPORTED               ──► [unsupported]     canned safe refusal
   │
   ▼
[validate]  ── evidence gate: intent must match record_type, else not grounded
   │
   ▼
[respond]   ── Ollama (gemma3:4b) writes an answer ONLY from the evidence
   │
   ▼
answer + intent + route + grounded flag + limitations
```

- **SQLite** holds exact structured data: menu, nutrition, offers, synthetic
  orders, legal footer lines, and RAG documents.
- **Chroma** holds searchable embeddings: menu, nutrition, offer, RAG, and
  legal documents (`record_type` metadata drives filtering).
- **LangGraph** orchestrates the deterministic routing workflow above.
- **Ollama** provides the local chat model (`gemma3:4b`) and the embedding
  model (`qwen3-embedding:0.6b`).
- **FastAPI** exposes `/health`, `/readiness`, `/chat`, and a static web UI.

---

## 3. Repository layout

```
.
├── config.py                  # central settings (models, paths, host, port, CORS)
├── agent/                     # LangGraph agent
│   ├── state.py               #   typed ChatState + Intent enum
│   ├── router.py              #   deterministic intent classification + entities
│   ├── evidence.py            #   evidence grounding gate
│   ├── responder.py           #   Ollama grounded answer generation
│   ├── graph.py               #   LangGraph nodes + orchestration
│   └── tools/
│       ├── sqlite_tools.py    #   SQLite lookups
│       └── chroma_retriever.py#   Chroma retrieval
├── api/
│   ├── main.py                # FastAPI app (health/readiness/chat)
│   └── static/index.html      # local chat web UI
├── database/                  # SQLite schema + loaders + verification
├── rag/                       # document building + Chroma ingestion
├── data_split/                # canonical source workbooks (two lanes)
│   ├── SQLITE_STRUCTURED/     #   exact/typed records
│   ├── CHROMA_EMBEDDINGS/     #   natural-language search documents
│   └── DATA_ROUTING_MANIFEST.md
├── sqlite_db/                 # generated database (gitignored) + schema.sql
├── chroma_db/                 # generated Chroma collection (gitignored)
├── tests/                     # pytest suite
├── prepare_package.py         # deployment packaging (checkpoints DB, zip)
└── .github/workflows/ci.yml   # CI (builds SQLite, runs pytest)
```

Generated databases (`sqlite_db/*.db`, `chroma_db/`) are intentionally **not**
committed. A fresh clone rebuilds them from the committed source workbooks.

---

## 4. Data flow

1. **Original sources** (kept outside the repo under `sources/`, `reports/`)
   are audited: menu CSV and nutrition booklet are cleaned and reconstructed
   into canonical records, with ambiguous nutrition rows quarantined.
2. **Master workbooks** (`data_split/`) split into two lanes:
   - `SQLITE_STRUCTURED` — exact fields, dates, statuses, and calculations.
   - `CHROMA_EMBEDDINGS` — natural-language text with metadata for retrieval.
3. **SQLite** is built from `SQLITE_STRUCTURED` (including `legal_docs` and
   `rag_documents`).
4. **Chroma** is built from `CHROMA_EMBEDDINGS` (menu, nutrition, offer, RAG,
   and legal sections) using `qwen3-embedding:0.6b`.
5. At runtime the agent grounds every answer in these two stores.

Data integrity rules (see `AGENTS.md`): never modify original sources, keep
source traceability metadata, quarantine ambiguous records, mark demo prices,
and answer only from retrieved evidence.

---

## 5. Requirements

- **Python 3.11+** (tested on 3.12/3.14)
- **Ollama** running locally with:
  - `gemma3:4b` (chat model)
  - `qwen3-embedding:0.6b` (embedding model)

Dependencies are pinned in `requirements.txt` (LangChain, LangGraph,
Chromadb, Ollama, FastAPI, Uvicorn, pydantic-settings, pandas, pytest).

---

## 6. Setup and run

```bash
git clone <repo-url> kfc-ai-chatbot
cd kfc-ai-chatbot
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env              # optional: adjust values
ollama pull gemma3:4b
ollama pull qwen3-embedding:0.6b
```

Build the data foundation:

```bash
python database/create_db.py        # create tables from schema.sql
python database/load_data.py        # load master workbooks into SQLite
python database/verify_db.py        # verify counts and sample rows
python rag/load_chroma.py           # embed documents into Chroma (needs Ollama)
python rag/verify_chroma.py         # verify the collection
```

Run the API:

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

- Chat UI: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`
- Readiness (SQLite + Chroma + Ollama + models): `http://127.0.0.1:8000/readiness`
- Chat API: `POST /chat` with `{"message": "..."}`

## 7. Tests

```bash
python -m pytest -q
```

The suite covers intent routing, evidence grounding, SQLite integrity,
Chroma coverage (including legal records), API health/readiness/validation,
config consistency, and startup from a non-root directory. Tests that need
generated databases or Ollama skip automatically when those prerequisites
are absent.

## 8. Deployment

```bash
python prepare_package.py
```

Checkpoints and closes SQLite (removing `-wal`/`-shm`), then writes
`kfc_chatbot_deploy.zip` containing code, data, and databases (caches, logs,
and `.env` excluded).

---

See also: [`README.md`](../README.md) (quick start), [`AGENTS.md`](../AGENTS.md)
(project rules), [`CONTRIBUTING.md`](../CONTRIBUTING.md) (development guide),
[`CHANGELOG.md`](../CHANGELOG.md) (release history).
