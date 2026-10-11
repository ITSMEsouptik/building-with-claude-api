"""Stream a reply with the SDK helper and measure time-to-first-token vs total time."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import log_usage, stream_chat

PROMPT = [{"role": "user", "content": "Explain what a context window is in about 120 words."}]


def main() -> None:
    """Print the reply as it arrives, then report TTFT, total latency and stop reason."""
    start = time.perf_counter()
    first_text_at: float | None = None
    with stream_chat(PROMPT, max_tokens=800) as stream:
        for text in stream.text_stream:
            if first_text_at is None:
                first_text_at = time.perf_counter() - start
            print(text, end="", flush=True)
        final = stream.get_final_message()
    total = time.perf_counter() - start

    print(f"\n\nTTFT (first text): {first_text_at:.2f}s | total: {total:.2f}s | stop_reason: {final.stop_reason}")
    log_usage(final)


if __name__ == "__main__":
    main()
