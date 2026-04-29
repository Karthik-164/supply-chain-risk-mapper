import logging
import os
import time
from typing import Any

import requests


logger = logging.getLogger(__name__)


class GroqClientError(RuntimeError):
    """Raised when the Groq API cannot return a valid response."""


class GroqClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://api.groq.com/openai/v1/chat/completions",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        if not self.api_key:
            raise GroqClientError("GROQ_API_KEY is not configured")

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                return self._parse_response(response.json())
            except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
                last_error = exc
                logger.exception("Groq request failed on attempt %s of %s", attempt, self.max_retries)
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)

        raise GroqClientError("Groq API request failed after retries") from last_error

    def _parse_response(self, data: dict[str, Any]) -> dict[str, Any]:
        message = data["choices"][0]["message"]
        return {
            "content": message["content"],
            "model": data.get("model", self.model),
            "usage": data.get("usage", {}),
        }
