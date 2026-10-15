# 04: Structured output

**What I learned:** tags + stop sequence and JSON schema are two ways to the same goal; neither replaces validation.

**What surprised me:** prefill, which older tutorials treat as the standard trick, is rejected outright on Haiku 5.5. JSON schema worked on the first try but cost 241 input tokens for a one-line prompt.

**Trade-offs:** tags + a stop sequence is cheap and works on every model, but relies on the model following the format, so validation is essential. Schema output is more reliable but constrains what the schema can express. Retries cost extra calls, so I keep them to one.

**Interview paragraph:** For extraction I define a pydantic model, get JSON via a schema or via tags with a stop sequence (prefill is not available on current models), and always validate before using it. Failures retry once and then raise a typed error, so bad output never silently flows downstream.

**Results:** *(paste pytest output and exercise success rate for each route)*