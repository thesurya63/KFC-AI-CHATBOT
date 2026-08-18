"""Agent graph node and grounding behavior tests (no Ollama required)."""
from agent import graph
from agent.state import Intent


def _order_state(order_id):
    return {
        "user_query": order_id,
        "normalized_query": order_id,
        "intent": Intent.ORDER_STATUS,
        "entities": {"order_id": order_id} if order_id else {},
        "evidence": [],
        "limitations": [],
    }


def test_order_found_is_grounded():
    state = graph.validate(graph.lookup_order(_order_state("KFC-ORDER-0001")))
    assert len(state["evidence"]) == 1
    assert state["grounded"] is True


def test_order_not_found_is_not_grounded():
    state = graph.validate(graph.lookup_order(_order_state("KFC-ORDER-9999")))
    assert state["evidence"] == []
    assert state["grounded"] is False
    assert state["limitations"]


def test_order_without_id_is_not_grounded():
    state = graph.validate(graph.lookup_order(_order_state(None)))
    assert state["grounded"] is False


def test_offer_start_date_limitation():
    state = graph.lookup_offer(
        {
            "intent": Intent.OFFER,
            "entities": {"offer_id": "KFC-OFFER-001"},
            "limitations": [],
        }
    )
    assert any("start date" in limitation.lower() for limitation in state["limitations"])


def test_unsupported_node_is_safe():
    state = graph.unsupported({"grounded": True})
    assert state["grounded"] is False
    assert state["answer"]


def test_route_by_intent_map():
    assert graph.route_by_intent({"intent": Intent.MENU_SEARCH}) == "search_menu"
    assert graph.route_by_intent({"intent": Intent.NUTRITION}) == "lookup_nutrition"
    assert graph.route_by_intent({"intent": Intent.ALLERGEN}) == "lookup_nutrition"
    assert graph.route_by_intent({"intent": Intent.OFFER}) == "lookup_offer"
    assert graph.route_by_intent({"intent": Intent.ORDER_STATUS}) == "lookup_order"
    assert graph.route_by_intent({"intent": Intent.DELIVERY_ISSUE}) == "lookup_order"
    assert graph.route_by_intent({"intent": Intent.LEGAL_POLICY}) == "search_legal"
    assert graph.route_by_intent({"intent": Intent.RECOMMENDATION}) == "recommend"
    assert graph.route_by_intent({"intent": Intent.UNSUPPORTED}) == "unsupported"