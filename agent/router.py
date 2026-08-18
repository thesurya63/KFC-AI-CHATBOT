"""Deterministic intent classification and routing for the KFC chatbot."""
import re
from agent.state import Intent


ORDER_ID_PATTERN = re.compile(r"KFC-ORDER-\d{4}", re.IGNORECASE)
OFFER_ID_PATTERN = re.compile(r"KFC-OFFER-\d{3}", re.IGNORECASE)
PRODUCT_ID_PATTERN = re.compile(r"KFC-MENU-\d{3}", re.IGNORECASE)

NUTRITION_KEYWORDS = ["calorie", "protein", "carb", "fat", "sugar", "nutrition", "kcal"]
# Use specific phrases for allergens to avoid matching ordinary food words
# e.g. "egg burger" should NOT trigger ALLERGEN, but "egg allergy" should
# Include both "contains" and "contain" (verb forms vary in natural questions)
ALLERGEN_KEYWORDS = [
    "allergen", "allergy", "allergic",
    "gluten-free", "gluten free", "contains gluten", "contain gluten",
    "nut allergy", "contains nuts", "contain nuts",
    "soy allergy", "contains soy", "contain soy",
    "dairy-free", "dairy free", "contains dairy", "contain dairy",
    "egg allergy", "contains egg", "contain egg", "msg",
]
# Use specific offer phrases so "Is this gluten-free?" does not trigger OFFER
# e.g. "free" alone is too broad; "free delivery" or "free item" is intentional
OFFER_KEYWORDS = [
    "offer", "coupon", "discount", "deal", "valid until", "promo",
    "free delivery", "free item", "buy one get one", "bogo",
]
ORDER_KEYWORDS = ["order", "delivery", "refund", "missing", "delay", "status"]
LEGAL_KEYWORDS = ["terms", "privacy", "disclaimer", "policy", "legal", "caution"]
RECOMMEND_KEYWORDS = ["recommend", "suggest", "best", "vegetarian option", "what should i"]


def classify_intent(query: str) -> tuple[Intent, float]:
    """Classify the user query into an intent with a confidence score."""
    q = query.lower()

    if ORDER_ID_PATTERN.search(q):
        return Intent.ORDER_STATUS, 0.98
    if OFFER_ID_PATTERN.search(q):
        return Intent.OFFER, 0.98
    if PRODUCT_ID_PATTERN.search(q):
        return Intent.MENU_DETAIL, 0.98

    if any(k in q for k in ALLERGEN_KEYWORDS):
        return Intent.ALLERGEN, 0.9
    if any(k in q for k in NUTRITION_KEYWORDS):
        return Intent.NUTRITION, 0.9
    if any(k in q for k in OFFER_KEYWORDS):
        return Intent.OFFER, 0.85
    # Recommendation before order so "what should I order" is a suggestion,
    # not an order-status query.
    if any(k in q for k in RECOMMEND_KEYWORDS):
        return Intent.RECOMMENDATION, 0.8
    if any(k in q for k in ORDER_KEYWORDS):
        return Intent.ORDER_STATUS, 0.8
    if any(k in q for k in LEGAL_KEYWORDS):
        return Intent.LEGAL_POLICY, 0.85

    return Intent.MENU_SEARCH, 0.6


def extract_entities(query: str) -> dict:
    """Extract key entities like order IDs, offer IDs, and product names."""
    entities = {}
    order_match = ORDER_ID_PATTERN.search(query)
    if order_match:
        entities["order_id"] = order_match.group(0).upper()
    offer_match = OFFER_ID_PATTERN.search(query)
    if offer_match:
        entities["offer_id"] = offer_match.group(0).upper()
    product_match = PRODUCT_ID_PATTERN.search(query)
    if product_match:
        entities["product_id"] = product_match.group(0).upper()
    return entities