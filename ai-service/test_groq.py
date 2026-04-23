import os
from dotenv import load_dotenv

from services.groq_client import GroqClient, GroqClientError


def main() -> int:
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY is not set. Add it to .env before running this test.")
        return 1

    client = GroqClient()
    result = client.chat_completion(
        messages=[
            {
                "role": "user",
                "content": "Reply with the single word: ok",
            }
        ],
        temperature=0,
        max_tokens=10,
    )
    print("Groq API call succeeded.")
    print(result["content"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GroqClientError as exc:
        print(f"Groq API call failed: {exc}")
        raise SystemExit(1) from exc
