# Security Review

## Executive Summary

Day 2 security documentation started for Tool-44 Supply Chain Risk Mapper. This file tracks AI-service threats, planned controls, test evidence, findings, residual risks, and team sign-off during the sprint.

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

### Day 7 OWASP ZAP Status

OWASP ZAP was not available in the current local environment, so a live scan and exported report could not be produced here.

## Findings Fixed

1. Added input sanitisation that strips HTML before request data is used.
2. Added rejection for empty JSON input.
3. Added rejection for obvious SQL injection patterns.
4. Added rejection for prompt injection attempts.
5. Added Flask rate limiting at 30 requests per minute.
6. Groq API calls already use retries, backoff, and error logging.

## Residual Risks

1. OWASP ZAP scan report is still pending because the tool is not installed in this environment.
2. Real endpoint-specific security validation for `/describe`, `/recommend`, and `/generate-report` depends on those routes being implemented.
3. Rate limiting currently uses in-memory storage, which is acceptable for local development but not ideal for a scaled deployment.

## Medium Fix Plan

1. Run OWASP ZAP after the full AI endpoints are available and export the report.
2. Review any Medium findings related to headers, information disclosure, or error responses.
3. Move rate-limit storage to Redis when the shared infrastructure is ready.

## Team Sign-Off

Detail not provided in document.
