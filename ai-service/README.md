# AI Service

## Overview

Flask-based AI microservice for Tool-44 Supply Chain Risk Mapper.

## Tech Stack

- Python 3.11+
- Flask 3.x
- Groq API
- flask-limiter

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key used for live AI calls |
| `GROQ_MODEL` | No | Model name, defaults to `llama-3.3-70b-versatile` |
| `RATE_LIMIT_STORAGE_URI` | No | Rate-limit storage URI, defaults to `memory://` |

## Install

```powershell
C:\Users\laksh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r ai-service\requirements.txt
```

## Run

```powershell
cd C:\internship_aaign\supply-chain-risk-mapper-main1\supply-chain-risk-mapper
C:\Users\laksh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe ai-service\app.py
```

Service URL:

```text
http://127.0.0.1:5000
```

## Health Check

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:5000/health -UseBasicParsing
```

## API Reference

### `POST /describe`

Request:

```json
{
  "input_text": "Port congestion is delaying supplier A shipments by five days."
}
```

Response:

```json
{
  "description": "Supplier disruption risk remains elevated due to shipment delays.",
  "generated_at": "2026-05-07T12:00:00+00:00",
  "model": "llama-3.3-70b-versatile",
  "is_fallback": false
}
```

### `POST /recommend`

Request:

```json
{
  "input_text": "Critical supplier delay affecting inbound inventory."
}
```

Response:

```json
[
  {
    "action_type": "monitor",
    "description": "Track delays daily.",
    "priority": "medium"
  },
  {
    "action_type": "review",
    "description": "Review alternate suppliers.",
    "priority": "high"
  },
  {
    "action_type": "communicate",
    "description": "Notify operations leads.",
    "priority": "medium"
  }
]
```

### `POST /generate-report`

Request:

```json
{
  "input_text": "Supplier disruption has increased lead times in the Asia route."
}
```

Response:

```json
{
  "title": "Supplier Risk Report",
  "summary": "Summary text.",
  "overview": "Overview text.",
  "key_items": ["A", "B", "C"],
  "recommendations": ["R1", "R2", "R3"],
  "generated_at": "2026-05-07T12:00:00+00:00",
  "model": "llama-3.3-70b-versatile",
  "is_fallback": false
}
```

### `GET /health`

Response:

```json
{
  "status": "ok",
  "model": "llama-3.3-70b-versatile",
  "avg_response_time_ms": 812.35,
  "uptime_seconds": 42.8
}
```

## Tests

Unit tests:

```powershell
C:\Users\laksh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest ai-service\tests -q -p no:cacheprovider
```

Security checks:

```powershell
C:\Users\laksh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe ai-service\run_security_checks.py
```

Live quality review:

```powershell
C:\Users\laksh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe ai-service\run_quality_review.py
```

Latest local results:

```text
describe: average_score_out_of_5=5.0
recommend: average_score_out_of_5=5.0
generate-report: average_score_out_of_5=5.0
```

## Notes

- The service returns fallback responses when Groq is unavailable.
- Input sanitisation blocks empty input, obvious SQL injection, and prompt injection patterns.
- Rate limiting is set to 30 requests per minute.
