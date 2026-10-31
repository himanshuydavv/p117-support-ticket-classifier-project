def get_sla(priority: str) -> dict:
    """
    Return SLA information based on ticket priority.
    """

    sla_rules = {
        "P1": {
            "response_time": "1 hour",
            "resolution_time": "4 hours"
        },
        "P2": {
            "response_time": "4 hours",
            "resolution_time": "24 hours"
        },
        "P3": {
            "response_time": "12 hours",
            "resolution_time": "48 hours"
        },
        "P4": {
            "response_time": "24 hours",
            "resolution_time": "72 hours"
        }
    }

    return sla_rules.get(
        priority,
        {
            "response_time": "24 hours",
            "resolution_time": "72 hours"
        }
    )