# Security Review

## Executive Summary

AI Developer 2 completed the local AI-service security implementation for Tool-44 Supply Chain Risk Mapper through the Day 14 deliverables that can be verified in this environment. The Flask service now enforces input sanitisation, injection rejection, rate limiting, Groq retry handling, fallback-safe responses, and automated verification for the implemented endpoints.

## Initial Threats

1. Prompt injection could cause the AI service to ignore project instructions or produce unsafe output.
2. Missing rate limiting could allow repeated requests to exhaust API quota or degrade service availability.
3. Secrets could be exposed if `.env` or API keys are committed to GitHub.
4. Unvalidated user input could introduce HTML/script content into prompts or responses.
5. Groq API failure or timeout could break user workflows if errors are not handled gracefully.

## Planned Controls

1. Add input sanitisation middleware and prompt-injection rejection.
2. Add `flask-limiter` at 30 requests per minute.
3. Keep `.env` ignored and use environment variables for secrets.
4. Validate endpoint inputs before calling the AI model.
5. Wrap Groq calls with retries, backoff, and logged errors.

## Test Evidence

### Day 5 Security Tests

Local security verification was run against the Flask middleware with `ai-service/run_security_checks.py`.

1. Empty JSON input is rejected with HTTP 400.
2. Obvious SQL injection payloads are rejected with HTTP 400.
3. Prompt injection payloads are rejected with HTTP 400.
4. HTML content is stripped before sanitized input is used.
5. Health endpoint continues to return HTTP 200.

### Day 8 Unit Tests

The AI service test suite covers:

1. `/health` response shape
2. `/describe` structured response format
3. `/recommend` structured response format
4. `/generate-report` structured response format
5. Groq fallback handling
6. Prompt injection rejection
7. SQL injection rejection
8. Empty-input rejection

Latest local result:

```text
8 passed in 0.65s
```

### Day 10 AI Quality Review

Live Groq-backed quality review was run with `ai-service/run_quality_review.py`.

Results saved in `ai-service/quality_review_results.json`:

1. `describe` average score: 5.0 / 5
2. `recommend` average score: 5.0 / 5
3. `generate-report` average score: 5.0 / 5

### Day 9 Security Sign-Off

1. Injection rejection verified locally for empty input, SQL injection, and prompt injection.
2. Rate limiting is configured at 30 requests per minute in the Flask app.
3. PII audit completed for local prompt templates and fallback templates.
4. JWT verification remains blocked because backend authentication is not implemented locally.

### Day 11 Live Endpoint Smoke Test

Live HTTP verification succeeded for:

1. `GET /health`
2. `POST /describe`
3. `POST /recommend`
4. `POST /generate-report`

### Day 11 Container Readiness

1. A real `ai-service/Dockerfile` is now present.
2. A real `docker-compose.yml` is now present for the AI service.
3. Live `docker-compose up` verification could not be run here because Docker is not installed in this environment.

### Day 7 OWASP ZAP Status

OWASP ZAP was not available in the current local environment, so a live scan and exported report could not be produced here.

## Findings Fixed

1. Added input sanitisation that strips HTML before request data is used.
2. Added rejection for empty JSON input.
3. Added rejection for obvious SQL injection patterns.
4. Added rejection for prompt injection attempts.
5. Added Flask rate limiting at 30 requests per minute.
6. Groq API calls already use retries, backoff, and error logging.
7. Added fallback-safe endpoint responses for live AI failures.
8. Added automated unit tests for format and rejection paths.

## Residual Risks

1. OWASP ZAP scan report is still pending because the tool is not installed in this environment.
2. JWT verification is blocked by missing backend authentication flow in the local environment.
3. Rate limiting currently uses in-memory storage, which is acceptable for local development but not ideal for a scaled deployment.
4. PII audit is limited to prompt templates and local payload handling; full system-wide verification depends on the backend/frontend integration.
5. Full-stack container rehearsal is blocked by the unfinished frontend/backend implementation and missing Docker runtime on this machine.

## Medium Fix Plan

1. Run OWASP ZAP after the full AI endpoints are available and export the report.
2. Review any Medium findings related to headers, information disclosure, or error responses.
3. Move rate-limit storage to Redis when the shared infrastructure is ready.
4. Verify JWT-protected Java-to-Flask integration once backend auth is implemented.

## Team Sign-Off

AI Developer 2 implementation and local verification completed.
Cross-team sign-off detail not provided in document.
