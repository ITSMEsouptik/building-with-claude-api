# 06: Prompt engineering

**What I learned:** the largest gain comes from defining terms and the output contract, not from clever tricks. Each technique should be an eval-measured change, added one at a time.

**What surprised me**
- Listing the JSON keys was not enough: `urgency: "high"` and free-form categories failed validation (0.000). Defining each value fixed it (0.972).
- XML tags and few-shot examples showed *no measurable gain* on my 12-case set: all three variants tied at 0.972. The honest conclusion is "dataset too easy/small", not "tags work".
- A "regression" I first measured for XML (0.806) was a truncation artifact from `max_tokens=400`.
- Prefill, the classic trick, is rejected on Haiku 5.5 (see lesson 04).

**Trade-offs**
- Longer prompts (rubric + examples) cost input tokens on every call. This is what prompt caching (lesson 12) is for.
- Examples calibrate judgement and format but can bias toward their labels and can leak into the eval if copied from it.
- XML adds structure and a clear data/instruction boundary at the price of a few tokens. It helps most with long, mixed-content prompts and with untrusted input.

**Interview paragraph:** I start with a clear, direct prompt that states the task, the exact output format, and definitions for every subjective label. I put untrusted input in tags and tell the model it is data. If errors remain on specific cases, I add a few diverse examples. Every step is scored on a fixed eval set so I can tell which change helped; if two variants tie, I extend the dataset instead of guessing.

## Exam-prep Q&A

- **Name the core techniques.** Be clear and direct; specify format; XML tags; multishot examples; role/system prompt; chain-of-thought / extended thinking; prefill (model-dependent).
- **Why XML tags?** Unambiguous section boundaries, easy to reference ("the text in `<email>`"), easy to parse output, separates data from instructions.
- **When use multishot?** When format or judgement is hard to describe, or edge cases are being missed. Use diverse examples, including a tricky one, and never reuse eval cases.
- **Prefill vs stop sequences?** Prefill starts the assistant turn to force format; a stop sequence ends generation at a delimiter. Prefill is rejected on some newer models, so prefer tags + stop sequence or JSON schema.
- **How reduce hallucination / injection?** Ask the model to answer only from supplied text, say untrusted content is data, tag it, validate outputs in code.
- **System prompt vs user prompt?** System sets role, rules, and persistent context; user carries the per-request task and data.
- **A new technique didn't change the score. Now what?** Check dataset size and difficulty; the eval may not discriminate. Grow it with hard cases before concluding.
- **Temperature?** Lower for extraction/classification, higher for creative work. (Not used in this repo; see Known issues.)

**Results:** `pytest 06_prompt_engineering`: 3 passed. Ladder: t0 0.000 -> t1 0.972 -> t2 0.972 -> t3 0.972.
