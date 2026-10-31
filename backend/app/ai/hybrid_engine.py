from backend.app.services.preprocess import preprocess_ticket
from backend.app.services.rule_engine import apply_rules
from backend.app.services.ml_classifier import predict_category
from backend.app.services.llm_fallback import classify_with_llm
from backend.app.services.sla import get_sla


def priority_value(priority: str) -> int:
    values = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4
    }

    return values.get(priority, 4)


def get_final_priority(rule_priority: str, ml_priority: str = "P4") -> str:
    """
    Select the more urgent priority.
    """

    if priority_value(rule_priority) < priority_value(ml_priority):
        return rule_priority

    return ml_priority


def classify_ticket(ticket: dict) -> dict:
    """
    Complete hybrid ticket classification pipeline.
    """

    # 1. Preprocess
    processed = preprocess_ticket(ticket)

    # 2. Rule engine
    rule_result = apply_rules(processed)

    # 3. ML category prediction
    ml_result = predict_category(processed["text"])

    # 4. LLM fallback for low-confidence prediction
    if ml_result["needs_fallback"]:
        llm_result = classify_with_llm(processed["text"])
        final_category = llm_result["category"]
        category_confidence = llm_result["confidence"]
        category_source = "llm"
    else:
        final_category = ml_result["category"]
        category_confidence = ml_result["confidence"]
        category_source = "ml"

    # 5. Final priority
    final_priority = rule_result["priority"]

    # 6. SLA
    sla = get_sla(final_priority)

    return {
        "category": final_category,
        "priority": final_priority,
        "confidence": category_confidence,
        "source": category_source,
        "escalated": rule_result["escalated"],
        "rule_reasons": rule_result["reasons"],
        "sla": sla
    }