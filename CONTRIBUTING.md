# Contributing

Thanks for your interest in the KFC RAG chatbot. This is an educational,
local-first project; contributions that keep it simple, readable, and grounded
in real data are welcome.

## Project principles

- **Ground every answer in data.** The agent must never invent menu, nutrition,
  offer, policy, or order facts. When evidence is missing, it reports a
  limitation.
- **Preserve source traceability.** Never modify the original Excel/CSV/PDF
  source files. Keep source-file and capture-date metadata.
- **Prefer simple, readable Python.** Small single-responsibility functions,
  type hints, `pathlib`, parameterized SQL. Avoid clever abstractions.
- **Centralize configuration.** Add new settings to `config.py` (and
  `.env.example`), not as hardcoded values.

## Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Pull the required Ollama models: `gemma3:4b` and `qwen3-embedding:0.6b`.
4. Build the data foundation (see `README.md`): `database/create_db.py`,
   `database/load_data.py`, then `rag/load_chroma.py` (requires Ollama).

## Making changes

1. Create a feature branch from `main`.
2. Write or update tests under `tests/`.
3. Run the suite: `python -m pytest -q`.
   - Tests that need generated databases or Ollama skip automatically when
     those prerequisites are absent, so the suite is always collectable.
4. Run the standalone smoke script: `python agent/test_agent.py`.
5. Update `CHANGELOG.md` and `README.md` if the change affects usage.

## Data integrity

- Never edit files under `sources/` or the original master workbooks.
- Offer start dates are not published in the source capture; responses must
  disclose this (handled by the offer limitation logic).
- Prices are demo/reference prices unless verified for a specific location.

## Pull request checklist

- [ ] Tests pass locally (`python -m pytest -q`)
- [ ] No secrets or `.env` files are committed
- [ ] No generated databases, caches, or logs are committed
- [ ] Configuration changes are reflected in `.env.example`
- [ ] README updated if behavior/usage changed

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
