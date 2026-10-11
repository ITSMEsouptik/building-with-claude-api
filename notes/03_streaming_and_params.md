# 03: Streaming and parameters

**What I learned:** streaming changes perceived latency (TTFT), not total time. The helper and raw events are two views of the same protocol. `stop_reason` tells me why generation ended.

**What surprised me:** *(fill in after running: how long TTFT was with thinking, how many thinking chars the raw stream showed)*

**Trade-offs:** streaming adds client complexity (partial output, mid-stream errors). A hard `max_tokens` cap bounds cost but can cut an answer mid-sentence. Stop sequences are cheaper than asking the model to stop, but they only fit predictable formats.

**Interview paragraph:** I stream when a person is waiting, because first-token latency matters more than total time. I use the SDK helper for the common path and raw events when I need to debug or handle block types myself. I always inspect `stop_reason`, so a truncated or stopped reply never gets treated as complete.

**Results:** *(paste measured TTFT/total and pytest output)*
