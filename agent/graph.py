"""LangGraph orchestration for the KFC chatbot agent."""
import re

from langgraph.graph import StateGraph, END

from agent.state import ChatState, Intent
from agent.router import classify_intent, extract_entities
from agent.tools import sqlite_tools, chroma_retriever
from agent.evidence import validate_evidence
from agent.responder import generate_answer

# Compile the graph once at module load — it never changes at runtime.
# Rebuilding it on every HTTP request wastes CPU on every chat call.
_compiled_graph: object = None


def _clean_terms(query: str, stopwords: set) -> list[str]:
    """Lowercase, strip punctuation, and drop stopwords from a query."""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", query.lower())
    return [word for word in cleaned.split() if word and word not in stopwords]


def normalize(state: ChatState) -> ChatState:
    """Normalize the query and classify intent."""
    query = state["user_query"].strip()
    intent, confidence = classify_intent(query)
    state["normalized_query"] = query
    state["intent"] = intent
    state["confidence"] = confidence
    state["entities"] = extract_entities(query)
    state["evidence"] = []
    state["limitations"] = []
    return state


def search_menu(state: ChatState) -> ChatState:
    """Search menu documents in Chroma."""
    results = chroma_retriever.search_menu(state["normalized_query"])
    state["retrieved_documents"] = results
    state["evidence"] = [
        {
            "source": "chroma",
            "record_id": r["metadata"].get("product_name", ""),
            "text": r["text"],
            "metadata": r["metadata"],
        }
        for r in results
    ]
    state["route"] = "chroma_menu"
    return state


def lookup_nutrition(state: ChatState) -> ChatState:
    """Look up nutrition or allergen records in SQLite.

    For ALLERGEN intent: searches the allergens column directly.
    For NUTRITION intent: searches by product_key to find the right row.
    If nothing is found, a limitation is recorded instead of falling back
    to menu data (which would mislabel menu rows as nutrition evidence).
    """
    query = state["normalized_query"]
    intent = state.get("intent")

    results = []

    if intent == Intent.ALLERGEN:
        # For allergen queries, search the allergens column directly
        stopwords = {"does", "contain", "is", "the", "a", "an", "in", "and",
                     "allergen", "allergy", "free", "safe", "have", "any"}
        terms = _clean_terms(query, stopwords)
        for term in terms:
            results = sqlite_tools.search_nutrition_by_allergen(term)
            if results:
                break
    else:
        # For nutrition queries, search by product key / product name
        stopwords = {"how", "many", "calories", "in", "the", "what", "is", "are",
                     "nutrition", "protein", "carbs", "fat", "sugar", "allergen",
                     "does", "contain", "kcal", "for", "of", "a", "an", "and"}
        terms = _clean_terms(query, stopwords)
        for term in terms:
            results = sqlite_tools.search_nutrition_by_key(term)
            if results:
                break

    # If no nutrition data was found, record a limitation rather than
    # falling back to menu data (which would mislabel it as nutrition).
    if not results:
        state["grounded"] = False
        state["limitations"] = state.get("limitations", []) + [
            "No nutrition or allergen data found for the requested product."
        ]
        state["sql_results"] = []
        state["evidence"] = []
        state["route"] = "sqlite_nutrition"
        return state

    state["sql_results"] = results
    state["evidence"] = [
        {
            "source": "sqlite",
            "record_id": r.get("record_id", r.get("product_id", "")),
            "text": str(r),
            "metadata": {"record_type": "nutrition"},
        }
        for r in results
    ]
    state["route"] = "sqlite_nutrition"
    return state


def lookup_offer(state: ChatState) -> ChatState:
    """Look up offers in SQLite."""
    offer_id = state["entities"].get("offer_id")
    if offer_id:
        results = [sqlite_tools.lookup_offer(offer_id)]
    else:
        results = sqlite_tools.list_active_offers()
    results = [r for r in results if r]
    state["sql_results"] = results
    state["evidence"] = [
        {
            "source": "sqlite",
            "record_id": r.get("offer_id", ""),
            "text": str(r),
            "metadata": {"record_type": "offer"},
        }
        for r in results
    ]
    # The source capture has no offer start dates; the responder must
    # tell the user when a start or end date is unavailable.
    limitations = state.get("limitations", [])
    if any(not r.get("valid_from") for r in results):
        limitations.append("Offer start dates are not available in the source data.")
    if any(not r.get("valid_to") for r in results):
        limitations.append(
            "Some offers do not publish an end date; do not describe them as permanently valid."
        )
    state["limitations"] = limitations
    state["route"] = "sqlite_offer"
    return state


def lookup_order(state: ChatState) -> ChatState:
    """Look up a synthetic order in SQLite."""
    order_id = state["entities"].get("order_id")
    result = sqlite_tools.lookup_order(order_id) if order_id else None
    state["sql_results"] = [result] if result else []
    state["evidence"] = [
        {
            "source": "sqlite",
            "record_id": result["order_id"],
            "text": str(result),
            "metadata": {"record_type": "order"},
        }
    ] if result else []
    state["route"] = "sqlite_order"
    return state


def search_legal(state: ChatState) -> ChatState:
    """Search legal/policy documents in Chroma."""
    results = chroma_retriever.search_all(state["normalized_query"])
    state["retrieved_documents"] = results
    state["evidence"] = [
        {
            "source": "chroma",
            "record_id": r["metadata"].get("product_name", ""),
            "text": r["text"],
            "metadata": r["metadata"],
        }
        for r in results
    ]
    state["route"] = "chroma_legal"
    return state


def recommend(state: ChatState) -> ChatState:
    """Hybrid recommendation: Chroma candidates + SQLite filters."""
    results = chroma_retriever.search_all(state["normalized_query"], n_results=5)
    state["retrieved_documents"] = results
    state["evidence"] = [
        {
            "source": "chroma",
            "record_id": r["metadata"].get("product_name", ""),
            "text": r["text"],
            "metadata": r["metadata"],
        }
        for r in results
    ]
    state["route"] = "hybrid_recommendation"
    return state


def unsupported(state: ChatState) -> ChatState:
    """Handle unsupported queries with a safe limitation."""
    state["grounded"] = False
    state["limitations"] = [
        "I can only answer questions about the KFC menu, nutrition, offers, and synthetic orders."
    ]
    state["answer"] = (
        "I'm sorry, I can only help with KFC menu items, nutrition facts, "
        "current demo offers, and synthetic order status. "
        "Please ask about one of those topics."
    )
    state["route"] = "unsupported"
    return state


def validate(state: ChatState) -> ChatState:
    """Validate evidence before generating a response."""
    return validate_evidence(state)


def respond(state: ChatState) -> ChatState:
    """Generate a grounded answer using Ollama."""
    if not state.get("grounded", False):
        if not state.get("answer"):
            state["answer"] = (
                "I could not find enough information to answer that question "
                "from the available KFC data."
            )
        return state
    state["answer"] = generate_answer(
        state["normalized_query"], state["evidence"], state["limitations"]
    )
    return state


def route_by_intent(state: ChatState) -> str:
    """Return the next node based on the classified intent."""
    intent = state["intent"]
    if intent == Intent.MENU_SEARCH:
        return "search_menu"
    if intent == Intent.MENU_DETAIL:
        return "search_menu"
    if intent == Intent.NUTRITION or intent == Intent.ALLERGEN:
        return "lookup_nutrition"
    if intent == Intent.OFFER:
        return "lookup_offer"
    if intent == Intent.ORDER_STATUS or intent == Intent.DELIVERY_ISSUE:
        return "lookup_order"
    if intent == Intent.LEGAL_POLICY:
        return "search_legal"
    if intent == Intent.RECOMMENDATION:
        return "recommend"
    return "unsupported"


def build_graph():
    """Build and return the compiled LangGraph."""
    graph = StateGraph(ChatState)

    graph.add_node("normalize", normalize)
    graph.add_node("search_menu", search_menu)
    graph.add_node("lookup_nutrition", lookup_nutrition)
    graph.add_node("lookup_offer", lookup_offer)
    graph.add_node("lookup_order", lookup_order)
    graph.add_node("search_legal", search_legal)
    graph.add_node("recommend", recommend)
    graph.add_node("unsupported", unsupported)
    graph.add_node("validate", validate)
    graph.add_node("respond", respond)

    graph.set_entry_point("normalize")
    graph.add_conditional_edges(
        "normalize",
        route_by_intent,
        {
            "search_menu": "search_menu",
            "lookup_nutrition": "lookup_nutrition",
            "lookup_offer": "lookup_offer",
            "lookup_order": "lookup_order",
            "search_legal": "search_legal",
            "recommend": "recommend",
            "unsupported": "unsupported",
        },
    )

    for node in [
        "search_menu",
        "lookup_nutrition",
        "lookup_offer",
        "lookup_order",
        "search_legal",
        "recommend",
        "unsupported",
    ]:
        graph.add_edge(node, "validate")
    graph.add_edge("validate", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


def run_agent(user_query: str) -> dict:
    """Run the agent on a user query and return the final state.

    The compiled graph is built once (on first call) and reused for every
    subsequent request — building it inside the function on every HTTP call
    wastes CPU since the graph structure never changes at runtime.
    """
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    result = _compiled_graph.invoke({"user_query": user_query})
    return {
        "answer": result.get("answer", ""),
        "intent": result.get("intent"),
        "route": result.get("route"),
        "grounded": result.get("grounded", False),
        "limitations": result.get("limitations", []),
        "evidence_count": len(result.get("evidence", [])),
    }