"""Intent classification and entity extraction tests."""
from agent.router import classify_intent, extract_entities
from agent.state import Intent


def test_menu_search():
    assert classify_intent("what burgers does KFC have")[0] == Intent.MENU_SEARCH


def test_nutrition():
    assert classify_intent("how many calories in Hot Wings")[0] == Intent.NUTRITION


def test_allergen():
    assert classify_intent("does the burger contain egg")[0] == Intent.ALLERGEN


def test_offer():
    assert classify_intent("is there a free delivery offer")[0] == Intent.OFFER


def test_offer_by_id():
    assert classify_intent("tell me about KFC-OFFER-002")[0] == Intent.OFFER


def test_order_by_id():
    assert classify_intent("where is KFC-ORDER-0001")[0] == Intent.ORDER_STATUS


def test_order_status():
    assert classify_intent("what is the delivery status")[0] == Intent.ORDER_STATUS


def test_legal_policy():
    assert classify_intent("tell me about terms and conditions")[0] == Intent.LEGAL_POLICY


def test_recommendation():
    assert classify_intent("what should I order")[0] == Intent.RECOMMENDATION


def test_extract_order_and_offer_ids():
    entities = extract_entities(
        "status of KFC-ORDER-1234 and offer KFC-OFFER-007"
    )
    assert entities["order_id"] == "KFC-ORDER-1234"
    assert entities["offer_id"] == "KFC-OFFER-007"