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

Detail not provided in document.

## Findings Fixed

Detail not provided in document.

## Residual Risks

Detail not provided in document.

## Team Sign-Off

Detail not provided in document.
