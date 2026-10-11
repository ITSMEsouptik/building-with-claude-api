# Lesson 03: Streaming and parameters

**What it is:** streaming returns a reply incrementally; `max_tokens` and `stop_sequences` control where it ends.

**When to use:** stream anything a person watches (chat UIs, long outputs). Use stop sequences to cut off structured or listy output early.

**Key points**
- TTFT is what users feel; total latency barely changes.
- SDK helper: `client.messages.stream(...)` with `text_stream` and `get_final_message()`. Raw: `stream=True` and handle events yourself.
- Events include `thinking_delta` before `text_delta` on models that think by default.
- `stop_reason` is one of `end_turn`, `max_tokens`, `stop_sequence`; check it every time.
- `max_tokens` is shared with thinking tokens.

**Common mistakes**
- Assuming the first delta is text.
- Reading usage before the stream finishes.
- Treating a `max_tokens` stop as a complete answer.
- Passing `temperature` (not supported by this SDK).
