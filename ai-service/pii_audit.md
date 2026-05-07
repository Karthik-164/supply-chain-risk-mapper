# PII Audit

## Scope

- Prompt templates in `ai-service/prompts`
- Request payload handling in `ai-service/app.py`
- Groq request construction in `ai-service/services/groq_client.py`

## Findings

1. Prompt templates do not hardcode personal data.
2. The application forwards request content supplied by the caller, so upstream systems must avoid sending personal data unnecessarily.
3. No static personal identifiers were found in the prompt templates or fallback responses.
4. Environment variables are used for secrets instead of source-controlled credentials.

## Conclusion

Local AI-service review found no hardcoded personal data in prompts or AI fallback templates.

## Residual Risk

Full system-wide PII verification remains dependent on backend and frontend payload shaping, which is not fully implemented in this environment.
