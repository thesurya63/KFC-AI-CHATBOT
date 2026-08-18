"""Typed state and intent definitions for the KFC chatbot agent."""
from enum import Enum
from typing import TypedDict, Optional


class Intent(str, Enum):
    """Supported user query intents."""
    MENU_SEARCH = "menu_search"
    MENU_DETAIL = "menu_detail"
    NUTRITION = "nutrition"
    ALLERGEN = "allergen"
    OFFER = "offer"
    ORDER_STATUS = "order_status"
    DELIVERY_ISSUE = "delivery_issue"
    LEGAL_POLICY = "legal_policy"
    RECOMMENDATION = "recommendation"
    UNSUPPORTED = "unsupported"


class EvidenceItem(TypedDict):
    """A single piece of grounded evidence."""
    source: str
    record_id: str
    text: str
    metadata: dict


class ChatState(TypedDict, total=False):
    """State that travels through the LangGraph."""
    user_query: str
    normalized_query: str
    intent: Intent
    confidence: float
    entities: dict
    route: str
    evidence: list[EvidenceItem]
    sql_results: list[dict]
    retrieved_documents: list[dict]
    answer: str
    citations: list[dict]
    error: Optional[str]
    grounded: bool
    limitations: list[str]