# 02: Multi-turn and system prompts

**What I learned:** the API is stateless and I own the conversation state. Roles must alternate. `system` is separate from `messages`.

**What surprised me:** `temperature` raised a `TypeError` because SDK 1.13.0 has no such argument, and newer models may reject it. I should check the installed SDK signature before using a parameter from memory.

**Trade-offs:** a longer window gives better recall but costs more input tokens and risks the context limit. A shorter window is cheaper but forgets, as in the "teal" demo. Summarizing old turns sits between the two.

**How I'd explain it in an interview:** The Messages API is stateless, so the client owns conversation state and resends it each call. I keep the message list explicit and bound it with a sliding window or summarization to control cost. The system prompt sets behavior separately from the history, and I version prompts so changes can be compared one at a time.

**Results:** *(paste the output of the exercise and pytest here)*
