import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
try:
    from google import genai
except ImportError:
    genai = None
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


def get_llm_client():
    """
    Create and return the OpenAI client.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured in the .env file."
        )

    return OpenAI(api_key=api_key)


def get_gemini_client():
    """
    Create and return the Gemini client.
    """

    if genai is None:
        raise ImportError(
            "google-genai is not installed. "
            "Install it with: pip install google-genai"
        )

    api_key = dotenv_values(PROJECT_ROOT / ".env").get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in the .env file."
        )

    return genai.Client(api_key=api_key)