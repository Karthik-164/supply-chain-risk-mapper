# Security Talking Points

- All JSON input is sanitized before it reaches the AI workflow.
- Empty input is rejected with HTTP 400.
- Obvious SQL injection patterns are rejected with HTTP 400.
- Prompt injection attempts are rejected with HTTP 400.
- The AI service is rate-limited to 30 requests per minute.
- The service keeps secrets in environment variables instead of source control.
