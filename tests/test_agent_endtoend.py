"""End-to-end agent grounding tests (require Ollama + local models)."""
import pytest

from agent.graph import run_agent
from helpers import requires_ollama


@requires_ollama
@pytest.mark.parametrize(
    "query,expect_grounded",
    [
        ("What burgers does KFC have?", True),
        ("How many calories in Hot Wings?", True),
        ("Does the burger contain egg?", True),
        ("What offers are available?", True),
        ("KFC-OFFER-001", True),
        ("KFC-ORDER-0001", True),
        ("Tell me about the terms and conditions", True),
    ],
)
def test_agent_grounds_known_queries(query, expect_grounded):
    result = run_agent(query)
    assert result["answer"], "expected a non-empty answer"
    assert result["grounded"] is expect_grounded


@requires_ollama
def test_agent_order_not_found_not_grounded():
    result = run_agent("KFC-ORDER-9999")
    assert result["grounded"] is False


@requires_ollama
def test_agent_legal_query_has_evidence():
    result = run_agent("Tell me about the terms and conditions")
    assert result["grounded"] is True
    assert result["evidence_count"] > 0