-- KFC RAG Chatbot SQLite Schema
-- Column names exactly match the validated Excel source files
-- to preserve source traceability (AGENTS.md rule 8).

PRAGMA journal_mode = WAL;

-- Menu items (from 01_Menu_Master.xlsx -> Menu sheet)
CREATE TABLE IF NOT EXISTS menu_items (
    product_id         TEXT PRIMARY KEY,
    product_name       TEXT NOT NULL,
    category           TEXT,
    description        TEXT,
    vegetarian_status  TEXT,
    calories           REAL,
    weight_g           REAL,
    serves             REAL,
    allergens          TEXT,
    price              REAL,
    price_status       TEXT,
    source_url         TEXT,
    captured_at        TEXT,
    raw_capture        TEXT
);

-- Reference prices (from Reference_Prices sheet)
CREATE TABLE IF NOT EXISTS reference_prices (
    reference_product_name TEXT PRIMARY KEY,
    reference_category     TEXT,
    reference_price_inr    REAL,
    source_pdf             TEXT
);

-- Nutrition records (from 02_Nutrition_Master.xlsx -> Nutrition sheet)
CREATE TABLE IF NOT EXISTS nutrition (
    record_id              TEXT PRIMARY KEY,
    product_key            TEXT,
    source_file            TEXT,
    category               TEXT,
    product_name           TEXT,
    avg_portion_weight_g   REAL,
    servings               REAL,
    energy_kcal            REAL,
    carbohydrate_g         REAL,
    protein_g              REAL,
    total_fat_g            REAL,
    total_fat_rda_pct      REAL,
    trans_fat_g            REAL,
    trans_fat_rda_pct      REAL,
    mufa_g                 REAL,
    pufa_g                 REAL,
    saturated_fat_g        REAL,
    saturated_fat_rda_pct  REAL,
    sodium_per_serve_g     REAL,
    sodium_per_100g_g      REAL,
    sodium_rda_pct         REAL,
    sugar_g                REAL,
    sugar_rda_pct          REAL,
    allergens              TEXT,
    msg_info               TEXT,
    caffeine_sweetener_info TEXT,
    review_status          TEXT,
    review_reason          TEXT
);

-- Offers (from 03_Offers_Legal_Master.xlsx -> Offers sheet)
CREATE TABLE IF NOT EXISTS offers (
    offer_id             TEXT PRIMARY KEY,
    offer_name           TEXT NOT NULL,
    description          TEXT,
    minimum_order_value  REAL,
    discount_type        TEXT,
    discount_value       REAL,
    free_item            TEXT,
    channel              TEXT,
    valid_from           TEXT,
    valid_to             TEXT,
    terms                TEXT,
    source_url           TEXT,
    captured_at          TEXT,
    validity_status      TEXT,
    verification_status  TEXT
);

-- Legal footer text (from Legal_Footer sheet, one row per capture line)
CREATE TABLE IF NOT EXISTS legal_docs (
    doc_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    line_number INTEGER,
    content     TEXT
);

-- 500 synthetic orders (from 04_Orders_Master.xlsx -> Synthetic_Orders sheet)
CREATE TABLE IF NOT EXISTS synthetic_orders (
    order_id                TEXT PRIMARY KEY,
    customer_id             TEXT,
    store_id                TEXT,
    order_time              TEXT,
    items                   TEXT,
    subtotal                REAL,
    discount                REAL,
    total_amount            REAL,
    payment_status          TEXT,
    order_status            TEXT,
    estimated_delivery_time TEXT,
    actual_delivery_time    TEXT,
    delay_reason            TEXT,
    missing_items           TEXT,
    refund_status           TEXT,
    delivery_partner        TEXT,
    synthetic_record        INTEGER
);

-- RAG documents (from 05_RAG_QA_Master.xlsx -> RAG_Documents sheet)
CREATE TABLE IF NOT EXISTS rag_documents (
    doc_id   TEXT PRIMARY KEY,
    doc_text TEXT NOT NULL,
    doc_meta TEXT
);