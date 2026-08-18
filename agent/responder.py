"""Ollama-based grounded response generation for the KFC chatbot."""
import json

import ollama

from config import settings

_client = ollama.Client(host=settings.OLLAMA_BASE_URL)

SYSTEM_PROMPT = """You are a helpful KFC customer service assistant.
Answer the user's question using ONLY the provided evidence below.
If the evidence does not contain the answer, say you do not have that information.
Do not invent facts about menu items, prices, nutrition, offers, or orders.
If a price is a reference/demo price, mention it is a demo reference price.
If the limitations say an offer start or end date is unavailable, state that clearly.
Keep your answer concise and friendly."""


def generate_answer(user_query: str, evidence: list[dict], limitations: list[str]) -> str:
    """Generate a grounded answer using the local Ollama model."""
    evidence_text = json.dumps(evidence, default=str, indent=2)
    limitation_text = "\n".join(limitations) if limitations else "None"

    user_prompt = f"""Question: {user_query}

Evidence:
{evidence_text}

Limitations:
{limitation_text}

Answer the question using only the evidence above."""

    response = _client.chat(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]