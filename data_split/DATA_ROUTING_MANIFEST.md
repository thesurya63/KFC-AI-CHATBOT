# KFC AI CHATBOT DATA ROUTING

CHROMA_EMBEDDINGS: searchable menu, nutrition, offers, legal, and RAG documents.
SQLITE_STRUCTURED: exact menu/nutrition/offer fields and synthetic orders.
REFERENCE_ONLY: raw sources, reports, diagrams, and audit material.

The same master workbook may intentionally exist in both lanes because it is represented as searchable text in Chroma and typed records in SQLite.
