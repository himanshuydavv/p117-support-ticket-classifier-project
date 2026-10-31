import re


def clean_text(text: str) -> str:
    """
    Clean ticket text before classification.
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove special characters
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_ticket(ticket: dict) -> dict:
    """
    Prepare a ticket for the AI/ML pipeline.
    """

    subject = clean_text(ticket.get("subject", ""))
    body = clean_text(ticket.get("body", ""))

    combined_text = f"{subject} {body}".strip()

    return {
        "subject": subject,
        "body": body,
        "text": combined_text,
        "channel": ticket.get("channel", ""),
        "customer_tier": ticket.get("customer_tier", ""),
    }