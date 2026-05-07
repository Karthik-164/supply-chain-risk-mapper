import html
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.groq_client import GroqClient, GroqClientError


load_dotenv()

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

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


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["PROMPTS_DIR"] = PROMPTS_DIR
    app.config["START_TIME"] = time.time()
    app.config["REQUEST_TIMINGS_MS"] = []
    app.config["AI_CLIENT"] = None

    Limiter(
        get_remote_address,
        app=app,
        default_limits=["30 per minute"],
        storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
    )

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
        timings = app.config["REQUEST_TIMINGS_MS"]
        avg_response_time_ms = round(sum(timings) / len(timings), 2) if timings else 0.0
        uptime_seconds = round(time.time() - app.config["START_TIME"], 2)
        client = app.config.get("AI_CLIENT")
        model = getattr(client, "model", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
        return {
            "status": "ok",
            "model": model,
            "avg_response_time_ms": avg_response_time_ms,
            "uptime_seconds": uptime_seconds,
        }

    @app.post("/describe")
    def describe():
        payload = get_request_payload()
        started_at = time.perf_counter()
        try:
            content, model = invoke_prompt(app, "describe_prompt.txt", payload, max_tokens=500)
            parsed = parse_json_output(content)
            response = {
                "description": parsed.get("description", content),
                "generated_at": utc_timestamp(),
                "model": model,
                "is_fallback": False,
            }
        except GroqClientError:
            response = fallback_describe(payload)
        record_timing(app, started_at)
        return jsonify(response)

    @app.post("/recommend")
    def recommend():
        payload = get_request_payload()
        started_at = time.perf_counter()
        try:
            content, _model = invoke_prompt(app, "recommend_prompt.txt", payload, max_tokens=700)
            parsed = parse_json_output(content)
            recommendations = parsed.get("recommendations")
            if not isinstance(recommendations, list):
                raise ValueError("recommendations missing from AI output")
            normalized = normalize_recommendations(recommendations)
            response = normalized[:3]
        except (GroqClientError, ValueError, TypeError):
            response = fallback_recommendations(payload)
        record_timing(app, started_at)
        return jsonify(response)

    @app.post("/generate-report")
    def generate_report():
        payload = get_request_payload()
        started_at = time.perf_counter()
        try:
            content, model = invoke_prompt(app, "generate_report_prompt.txt", payload, max_tokens=1000)
            parsed = parse_json_output(content)
            response = normalize_report(parsed)
            response["generated_at"] = utc_timestamp()
            response["model"] = model
            response["is_fallback"] = False
        except (GroqClientError, ValueError, TypeError):
            response = fallback_report(payload)
        record_timing(app, started_at)
        return jsonify(response)

    return app


def get_ai_client(app: Flask) -> GroqClient:
    client = app.config.get("AI_CLIENT")
    if client is None:
        client = GroqClient()
        app.config["AI_CLIENT"] = client
    return client


def get_request_payload() -> dict[str, Any]:
    payload = getattr(g, "sanitized_json", None)
    if not isinstance(payload, dict):
        return {}
    return payload


def invoke_prompt(app: Flask, prompt_filename: str, payload: dict[str, Any], max_tokens: int) -> tuple[str, str]:
    prompt_text = load_prompt(prompt_filename)
    user_context = json.dumps(payload, ensure_ascii=True, indent=2)
    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": f"Project data:\n{user_context}"},
    ]
    result = get_ai_client(app).chat_completion(messages=messages, temperature=0.3, max_tokens=max_tokens)
    return result["content"], result["model"]


def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8").strip()


def parse_json_output(content: str) -> dict[str, Any]:
    return json.loads(content)


def normalize_recommendations(recommendations: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in recommendations:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "action_type": str(item.get("action_type", "monitor")),
                "description": str(item.get("description", "Detail not provided in document.")),
                "priority": str(item.get("priority", "medium")),
            }
        )
    if len(normalized) < 3:
        normalized.extend(fallback_recommendations({})[: 3 - len(normalized)])
    return normalized


def normalize_report(parsed: dict[str, Any]) -> dict[str, Any]:
    key_items = parsed.get("key_items", [])
    recommendations = parsed.get("recommendations", [])
    if not isinstance(key_items, list) or not isinstance(recommendations, list):
        raise ValueError("Invalid report format")
    return {
        "title": str(parsed.get("title", "Supply Chain Risk Report")),
        "summary": str(parsed.get("summary", "Summary unavailable.")),
        "overview": str(parsed.get("overview", "Overview unavailable.")),
        "key_items": [str(item) for item in key_items],
        "recommendations": [str(item) for item in recommendations],
    }


def fallback_describe(payload: dict[str, Any]) -> dict[str, Any]:
    subject = extract_subject(payload)
    return {
        "description": f"Fallback description generated for {subject}. Manual review recommended.",
        "generated_at": utc_timestamp(),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "is_fallback": True,
    }


def fallback_recommendations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    subject = extract_subject(payload)
    return [
        {
            "action_type": "monitor",
            "description": f"Monitor {subject} for new delays or supplier disruptions.",
            "priority": "medium",
        },
        {
            "action_type": "review",
            "description": f"Review upstream dependency data for {subject} before escalation.",
            "priority": "high",
        },
        {
            "action_type": "communicate",
            "description": f"Share a fallback plan for {subject} with the operations team.",
            "priority": "medium",
        },
    ]


def fallback_report(payload: dict[str, Any]) -> dict[str, Any]:
    subject = extract_subject(payload)
    return {
        "title": f"Fallback Supply Chain Report for {subject}",
        "summary": "The AI service returned a fallback report because the live model response was unavailable.",
        "overview": f"This report captures a fallback overview for {subject} and should be manually reviewed.",
        "key_items": [
            "Validate the underlying supplier and shipment inputs.",
            "Confirm disruption status with the operations team.",
            "Review alternative sourcing options if delays continue.",
        ],
        "recommendations": [
            "Retry the AI workflow after service recovery.",
            "Escalate to manual review if the issue is time-sensitive.",
            "Record the fallback event for audit visibility.",
        ],
        "generated_at": utc_timestamp(),
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "is_fallback": True,
    }


def extract_subject(payload: dict[str, Any]) -> str:
    for key in ("input_text", "supplier", "name", "title", "risk"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "the submitted request"


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


def record_timing(app: Flask, started_at: float) -> None:
    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    timings = app.config["REQUEST_TIMINGS_MS"]
    timings.append(elapsed_ms)
    if len(timings) > 100:
        del timings[:-100]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
