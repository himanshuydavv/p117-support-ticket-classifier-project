from backend.app.services.ml_classifier import predict_category


def main():
    test_tickets = [
        "I was charged twice for my order",
        "I cannot log into my account",
        "My package has not arrived",
        "The application keeps crashing",
        "I want more information about your service"
    ]

    for ticket in test_tickets:
        result = predict_category(ticket)

        print("\nTicket:", ticket)
        print("Category:", result["category"])
        print("Confidence:", round(result["confidence"], 3))
        print("Source:", result["source"])
        print("Needs Fallback:", result["needs_fallback"])


if __name__ == "__main__":
    main()