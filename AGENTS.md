# KFC RAG Chatbot — Agent Instructions

## 1. Clear project goal

Build a beginner-friendly local KFC customer-support and menu chatbot as a learning project.

The chatbot agent should behave like a highly helpful, friendly customer service assistant for KFC. It should focus on accurate answers about store policies, menu items, nutrition, offers, and order statuses.

The final project should allow a customer to:

- search KFC products, categories, descriptions, and prices;
- ask for nutrition facts and allergens;
- ask about current demo offers, terms, and validity dates;
- ask about a synthetic order using an order ID;
- check synthetic delivery status, delay reasons, missing items, and refund status;
- receive recommendations grounded in the available KFC data.

The system must use:

- Python for data preparation and application logic;
- SQLite for exact structured data and order lookups;
- Chroma for searchable document embeddings;
- LangChain and LangChain Community for loaders, documents, embeddings, and retrieval;
- LangGraph for explicit agent workflow and query routing;
- Ollama for a local free language model and embedding model;
- FastAPI later for the local chatbot API.

This is a local educational demonstration, not a real KFC production system. Orders are synthetic. Prices are demo or reference prices unless a location-specific official source verifies them.

The chatbot must strictly use retrieved information from the approved knowledge bases and structured databases. It must ground every response in available data and avoid hallucinations.

## 2. Overarching goals

Always follow these goals in priority order:

1. Teach the user while building the project.

3. Preserve source traceability and data accuracy.
4. Build and test the data foundation before adding AI agents.
5. Prefer simple readable Python over clever or overly abstract code.
6. Never invent missing menu, nutrition, offer, or order facts.
7. Make every result reproducible and easy for a beginner to inspect.

## 3. Operating context

The active coding workspace is:

`G:\Projects\KFC AI CHATBOT\kfc-rag-chatbot-code`

The project data is divided into:

- `data_split/SQLITE_STRUCTURED` — data for exact fields, dates, status, and calculations;
- `data_split/CHROMA_EMBEDDINGS` — data for natural-language search and grounding;
- `data_split/DATA_ROUTING_MANIFEST.md` — explanation of the split;
- `sqlite_db` — generated SQLite database files;
- `chroma_db` — generated Chroma files;
- `ingestion` — data reading, cleaning, and validation code;
- `database` — SQLite schema, loaders, and query helpers;
- `rag` — document creation, embeddings, Chroma, and retrieval;
- `agent` — LangGraph state and routing;
- `api` — FastAPI endpoints;
- `tests` — verification tests;
- `config` — readable configuration files.

Do not rely on files outside the coding workspace unless the user explicitly approves it. The parent project contains originals and reference materials that must be preserved.

## 4. Permission and safety rules

### Approval is required for every action

Before performing any material action, explain what will happen and ask the user for approval. This includes:

- creating a file or folder;
- editing any file;
- deleting, moving, renaming, or overwriting anything;
- copying project data;
- installing or changing packages;
- running a command or script that changes files or databases;
- creating or changing SQLite tables;
- creating or rebuilding Chroma collections;
- changing configuration;
- continuing to the next milestone.

Read-only inspection may be proposed first, but ask approval before running it when the action is outside the current approved step.

Never assume that approval for one file grants approval for another file. Ask again when the target or action changes.

Never delete, move, rename, or overwrite a file without explicit approval for that exact action and target.

If approval is unclear, stop and ask. Do not guess.



## 6. Recommended Python style

Use clean, readable Python that follows this structure:

1. imports;
2. constants and configuration;
3. small functions with one responsibility;
4. a `main()` function;
5. `if __name__ == "__main__": main()`.

Prefer:

- type hints for function inputs and outputs;
- descriptive variable names;
- small functions of about 10–25 lines;
- standard library code where practical;
- comments explaining why, not obvious line-by-line narration;
- parameterized SQL queries;
- `pathlib.Path` for file paths;
- explicit error messages;
- reusable functions instead of duplicated code.

Avoid:

- one giant script;
- unexplained abbreviations;
- hidden global state;
- hardcoded absolute paths;
- unsafe SQL string formatting;
- unnecessary classes or advanced patterns;
- modifying source Excel files.

## 7. Required build order

Work through one approved milestone at a time:

1. Read and inspect the menu workbook.
2. Validate menu columns, IDs, prices, names, and missing values.
3. Create the SQLite database file with approval.
4. Create the `products` table with approval.
5. Insert validated menu records with approval.
6. Run simple SQL queries and inspect results.
7. Add nutrition data.
8. Add offers and validity checks.
9. Add synthetic orders and order queries.
10. Prepare Chroma documents.
11. Generate embeddings and persist Chroma.
12. Build LangGraph routing.
13. Connect Ollama.
14. Add FastAPI.
15. Add tests and a local demo interface.

Do not move to the next milestone until the current milestone is explained, approved, executed, and verified.

## 8. Data integrity rules

- Never modify original Excel, CSV, text, PDF, or report files.
- Preserve source file, sheet, row, URL, and capture-date metadata.
- Keep ambiguous nutrition records quarantined.
- Mark prices as `DEMO_REFERENCE_PRICE` unless officially verified for a location.
- Use SQLite for exact prices, dates, calculations, order status, and missing items.
- Use Chroma for natural-language descriptions and retrieval context.
- Use the LLM to explain verified results, not to invent facts.
- Answer only from retrieved knowledge-base records or SQLite query results.
- Ground menu, nutrition, offer, policy, and order-status answers in the data before responding.
- Do not make up store policies, prices, delivery promises, discounts, ingredients, allergens, or order updates.
- If evidence is missing or conflicting, return a clear limitation.

## 9. Required verification after every step

Before asking permission to continue, report:

- files read or changed;
- rows read and written;
- validation checks performed;
- errors or unresolved records;
- one or two representative outputs;
- whether the original data remained unchanged.

The agent must stop after this report and wait for user approval.
