from backend.app.ai.llm_client import get_llm_client


def main():
    client = get_llm_client()

    print("Provider:", client["provider"])
    print("API key loaded successfully:", bool(client["api_key"]))


if __name__ == "__main__":
    main()