# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Central `config.py` (pydantic-settings) as the single source of truth for
  models, paths, host, port, and CORS.
- `/readiness` endpoint that checks SQLite, Chroma, and Ollama model
  availability; `/health` now reports the configured chat model.
- Legal documents ingested into Chroma with `record_type="legal"` so
  legal-policy queries can be grounded.
- `legal_docs` and `rag_documents` SQLite tables are now populated.
- Full pytest suite under `tests/` (config, router, evidence, graph nodes,
  SQLite integrity, Chroma coverage, API, end-to-end, and startup-from-any-dir).
- `prepare_package.py` deployment packaging (checkpoints the DB, removes
  `-wal`/`-shm` files, writes `kfc_chatbot_deploy.zip`).
- GitHub Actions CI workflow and standard repo files (LICENSE, CONTRIBUTING,
  CHANGELOG, .gitattributes).

### Changed
- Model configuration aligned across all modules (`gemma3:4b` chat,
  `qwen3-embedding:0.6b` embeddings) and centralized.
- File paths are now independent of the working directory.
- CORS restricted to configured origins instead of the wildcard default.
- `rag/load_chroma.py` performs a clean rebuild and fixes RAG document parsing.
- Offer responses now disclose when start/end dates are unavailable.
- Requirements pinned to verified versions.

### Fixed
- Nutrition/allergen term matching now strips punctuation (e.g. `egg?`).
- "what should I order" routes to recommendation instead of order status.
