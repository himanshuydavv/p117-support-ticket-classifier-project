from backend.app.ai.llm_client import get_gemini_client


CATEGORIES = [
    "billing",
    "technical",
    "account",
    "shipping",
    "general"
]


def classify_with_llm(ticket_text: str) -> dict:
    """
    Classify a support ticket using the LLM.
    """

    client = get_gemini_client()

    prompt = f"""
You are a customer support ticket classifier.

Classify the ticket into exactly ONE of these categories:

billing
technical
account
shipping
general

Ticket:
{ticket_text}

Return only one category name from the allowed categories.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"temperature": 0},
    )

    category = response.text.strip().lower()

    # Validate the LLM response
    if category not in CATEGORIES:
        category = "general"

    return {
        "category": category,
        "confidence": 1.0,
        "source": "llm"
    }