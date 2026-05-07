# AI Talking Points

## Groq In Plain English

Groq is the hosted AI provider used by this project. The service sends structured prompts and expects structured JSON back so the application can show predictable results to the user.

## Prompt Explanation

Each endpoint uses a dedicated prompt template:

- `/describe` asks for a short risk description
- `/recommend` asks for exactly 3 actionable recommendations
- `/generate-report` asks for a full structured report

## Reliability Notes

- The service retries Groq calls up to 3 times with backoff.
- If Groq still fails, the service returns a fallback response instead of a server error.
