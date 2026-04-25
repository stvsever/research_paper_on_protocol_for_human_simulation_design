# OpenRouter Validation Notes

Validation date: 2026-04-25

The repository `.env` file was checked locally and contains an `OPENROUTER_API_KEY` entry. The key value, key label, and account metadata are not stored in this repository.

Sanitized validation results:

- `https://openrouter.ai/api/v1/key` returned HTTP 200 using the configured key.
- The OpenRouter models endpoint listed all preregistered pilot model IDs:
  - `meta-llama/llama-3.2-1b-instruct`
  - `meta-llama/llama-3.2-3b-instruct`
  - `google/gemma-2-27b-it`
  - `openai/gpt-4o-mini`
  - `openai/gpt-5`

If a selected model becomes unavailable at execution time, use the preregistered nearest-available-model replacement rule and log the replacement in `src/preregistration/deviations.md` before analyzing pilot outcomes.

