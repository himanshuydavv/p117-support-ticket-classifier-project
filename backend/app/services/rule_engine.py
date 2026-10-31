def apply_rules(ticket: dict) -> dict:
    """
    Apply rule-based checks for priority and escalation.
    """

    subject = ticket.get("subject", "").lower()
    body = ticket.get("body", "").lower()
    customer_tier = ticket.get("customer_tier", "").lower()

    text = f"{subject} {body}"

    priority = "P4"
    reasons = []

    # VIP customer rule
    if customer_tier == "vip":
        priority = "P2"
        reasons.append("VIP customer")

    # Critical keywords
    critical_keywords = [
        "outage",
        "chargeback",
        "legal",
    ]

    for keyword in critical_keywords:
        if keyword in text:
            priority = "P1"
            reasons.append(f"Critical keyword: {keyword}")

    # High-priority keywords
    high_priority_keywords = [
        "refund",
        "payment failed",
        "cannot login",
        "crash",
        "not working",
    ]

    for keyword in high_priority_keywords:
        if keyword in text and priority != "P1":
            priority = "P2"
            reasons.append(f"High priority keyword: {keyword}")

    return {
        "priority": priority,
        "escalated": priority == "P1",
        "reasons": reasons,
        "source": "rule_engine",
    }