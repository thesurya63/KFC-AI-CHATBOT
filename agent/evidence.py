"""Evidence validation gate for the KFC chatbot agent."""
from agent.state import ChatState, Intent


def validate_evidence(state: ChatState) -> ChatState:
    """Validate that evidence is sufficient and consistent for the intent."""
    intent = state.get("intent")
    evidence = state.get("evidence", [])
    limitations = state.get("limitations", [])

    # No evidence at all
    if not evidence:
        state["grounded"] = False
        state["limitations"] = limitations + [
            "No supporting evidence was found for this question."
        ]
        return state

    # Check evidence matches the intent type
    expected_type = _expected_record_type(intent)
    if expected_type:
        matching = [e for e in evidence if e.get("metadata", {}).get("record_type") == expected_type]
        if not matching:
            state["grounded"] = False
            state["limitations"] = limitations + [
                f"No {expected_type} evidence matched this question."
            ]
            return state

    state["grounded"] = True
    state["limitations"] = limitations
    return state


def _expected_record_type(intent: Intent) -> str | None:
    """Map an intent to the expected evidence record_type, if any."""
    if intent in (Intent.MENU_SEARCH, Intent.MENU_DETAIL, Intent.RECOMMENDATION):
        return "menu"
    # Both nutrition and allergen queries are answered from the nutrition table
    if intent in (Intent.NUTRITION, Intent.ALLERGEN):
        return "nutrition"
    if intent == Intent.OFFER:
        return "offer"
    if intent == Intent.LEGAL_POLICY:
        return "legal"
    return None