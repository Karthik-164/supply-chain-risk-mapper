import html
import os
import re
from typing import Any

from flask import Flask, g, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
)

PROMPT_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bignore (all )?(previous|prior|above) instructions\b",
        r"\bdisregard (all )?(previous|prior|above) instructions\b",
        r"\breveal (the )?(system|developer|hidden) prompt\b",
        r"\bshow (me )?(the )?(system|developer|hidden) prompt\b",
        r"\byou are now\b",
        r"\bjailbreak\b",
        r"\bprompt injection\b",
    ]
]


def contains_prompt_injection(value: Any) -> bool:
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in PROMPT_INJECTION_PATTERNS)
    if isinstance(value, list):
        return any(contains_prompt_injection(item) for item in value)
    if isinstance(value, dict):
        return any(contains_prompt_injection(item) for item in value.values())
    return False


def strip_html(value: Any) -> Any:
    if isinstance(value, str):
        without_tags = re.sub(r"<[^>]*>", "", value)
        return html.unescape(without_tags).strip()
    if isinstance(value, list):
        return [strip_html(item) for item in value]
    if isinstance(value, dict):
        return {key: strip_html(item) for key, item in value.items()}
    return value


@app.before_request
def sanitize_json_input():
    if not request.is_json:
        return None

    payload = request.get_json(silent=True)
    if payload is None:
        return None

    if contains_prompt_injection(payload):
        return jsonify({"error": "Prompt injection detected"}), 400

    g.sanitized_json = strip_html(payload)
    return None


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
