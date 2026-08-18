"""End-to-end test of the KFC chatbot agent."""
import sys
from agent.graph import run_agent

sys.stdout.reconfigure(encoding="utf-8")

QUERIES = [
    "What burgers does KFC have?",
    "How many calories in Hot Wings?",
    "What offers are available?",
    "KFC-ORDER-0001",
    "What is the delivery status of my order?",
    "Tell me about the terms and conditions",
    "What is the weather today?",
]


def main() -> None:
    """Run the agent on sample queries and print results."""
    for q in QUERIES:
        result = run_agent(q)
        print(f"\nQ: {q}")
        print(f"  Intent: {result['intent']}")
        print(f"  Route: {result['route']}")
        print(f"  Grounded: {result['grounded']}")
        print(f"  Evidence: {result['evidence_count']}")
        print(f"  Answer: {result['answer'][:200]}")
        if result["limitations"]:
            print(f"  Limitations: {result['limitations']}")


if __name__ == "__main__":
    main()