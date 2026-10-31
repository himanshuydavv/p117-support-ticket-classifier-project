from backend.app.ai.llm_client import get_gemini_client


def draft_reply(ticket_text: str, knowledge_articles: list) -> str:
    """
    Generate a professional customer support reply
    using knowledge-base context.
    """

    # Prepare knowledge-base context
    context_parts = []

    for article in knowledge_articles:

        title = article.get("title", "Untitled")
        body = article.get("body", "")

        context_parts.append(
            f"Title: {title}\n"
            f"Content: {body}"
        )

    context = "\n\n".join(context_parts)

    # Prompt
    prompt = f"""
You are a customer support assistant.

Write a helpful, professional and concise reply
to the customer.

Customer ticket:
{ticket_text}

Knowledge base:
{context}

Rules:
- Use only information available in the knowledge base.
- Do not invent policies or information.
- Be concise and professional.
- Do not claim that an action has been completed
  unless the ticket explicitly says so.
- If the knowledge base does not contain enough
  information, clearly say that the issue needs
  further review.
"""

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        reply = response.text

        if not reply:
            return "Unable to generate a suggested reply."

        return reply.strip()

    except Exception:
        return (
            "Unable to generate an AI suggested reply with Gemini. "
            "Please try again later."
        )