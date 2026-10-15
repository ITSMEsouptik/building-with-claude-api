# Lesson 04: Structured output

**What it is:** getting machine-readable output (JSON) that parses and validates.

**When to use:** extraction, classification, anything a program consumes.

**Key points**
- Tags + stop sequence: ask for `<json>...</json>` and set `stop_sequences=["</json>"]`. The matched stop text is excluded from the reply.
- JSON schema: `output_config={"format": {"type": "json_schema", "schema": ...}}`.
- Always validate with pydantic and handle failures: retry, then raise.
- Check `stop_reason`: `max_tokens` means the JSON may be cut off.

**Common mistakes**
- Trusting output without validation.
- `max_tokens` too low, so JSON truncates (thinking can share the budget).
- Putting numeric bounds in the schema when the API may not support them. Validate in code instead.
- Prefill is rejected by Haiku 5.5 (400: "This model does not support assistant message prefill"), so the conversation must end with a user message.
- JSON schema works but adds input tokens (241 for a one-line prompt in my probe).
