import os
import sys
import requests
from dotenv import load_dotenv

def main() -> int:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        print("GROQ_API_KEY is not set. Add it to .env before running this test.")
        return 1

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with the single word: ok",
                }
            ],
            "temperature": 0,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print("Groq API call succeeded.")
    print(content)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Groq API call failed: {exc}")
        raise SystemExit(1) from exc
