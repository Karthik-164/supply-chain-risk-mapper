# Lessons Learned

## What Worked

- Building a reusable Groq client early made later endpoint work simpler.
- Strict JSON prompts made response handling more predictable.
- Adding local security checks early made the Flask middleware easier to verify.

## What Needs Improvement

- Java and Docker dependencies should be installed earlier to reduce integration delay.
- The full OWASP ZAP workflow should be available before final security sign-off.
- Prompt quality review needs both structural checks and human semantic review.

## Future Sprint Ideas

- Add Redis-backed rate-limit storage.
- Add richer prompt templates with domain examples.
- Add persistent AI quality-reporting dashboards.
