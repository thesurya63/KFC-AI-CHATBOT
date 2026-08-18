"""Evidence validation gate tests."""
from agent.evidence import validate_evidence
from agent.state import Intent


def _state(intent, evidence, limitations=None):
    return {"intent": intent, "evidence": evidence, "limitations": limitations or []}


def _evidence(record_type):
    return [
        {"source": "sqlite", "record_id": "x", "text": "body", "metadata": {"record_type": record_type}}
    ]


def test_no_evidence_not_grounded():
    state = validate_evidence(_state(Intent.NUTRITION, []))
    assert state["grounded"] is False
    assert state["limitations"]


def test_wrong_record_type_not_grounded():
    state = validate_evidence(_state(Intent.NUTRITION, _evidence("menu")))
    assert state["grounded"] is False


def test_matching_record_type_grounded():
    state = validate_evidence(_state(Intent.NUTRITION, _evidence("nutrition")))
    assert state["grounded"] is True


def test_menu_intent_expects_menu():
    assert validate_evidence(_state(Intent.MENU_SEARCH, _evidence("menu")))["grounded"] is True


def test_legal_intent_requires_legal_evidence():
    assert validate_evidence(_state(Intent.LEGAL_POLICY, _evidence("menu")))["grounded"] is False
    assert validate_evidence(_state(Intent.LEGAL_POLICY, _evidence("legal")))["grounded"] is True