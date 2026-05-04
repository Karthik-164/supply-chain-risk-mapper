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

SQL_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"(--|#|/\*|\*/|;)",
        r"\b(drop|delete|truncate|alter|union\s+select|insert\s+into|update\s+\w+\s+set)\b",
        r"(\bor\b|\band\b)\s+\d+\s*=\s*\d+",
        r"'[\s]*or[\s]+'?1'?\s*=\s*'?1",
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


def contains_sql_injection(value: Any) -> bool:
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in SQL_INJECTION_PATTERNS)
    if isinstance(value, list):
        return any(contains_sql_injection(item) for item in value)
    if isinstance(value, dict):
        return any(contains_sql_injection(item) for item in value.values())
    return False


def has_empty_input(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0 or any(has_empty_input(item) for item in value)
    if isinstance(value, dict):
        return len(value) == 0 or any(has_empty_input(item) for item in value.values())
    return value is None


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

    sanitized_payload = strip_html(payload)

    if has_empty_input(sanitized_payload):
        return jsonify({"error": "Empty input is not allowed"}), 400

    if contains_sql_injection(sanitized_payload):
        return jsonify({"error": "SQL injection pattern detected"}), 400

    if contains_prompt_injection(sanitized_payload):
        return jsonify({"error": "Prompt injection detected"}), 400

    g.sanitized_json = sanitized_payload
    return None


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
