"""Raw streaming: handle each server-sent event yourself to see the protocol."""
import sys
import time
from pathlib import Path

from anthropic.types import MessageParam

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import get_client

PROMPT: list[MessageParam] = [{"role": "user", "content": "Name three uses of a hash map, one line each."}]


def main() -> None:
    """Consume raw events, separating thinking text from answer text, and log event timing."""
    start = time.perf_counter()
    answer: list[str] = []
    thinking_chars = 0
    stop_reason = None
    usage = None

    stream = get_client().messages.create(
        model="claude-haiku-5-5", max_tokens=800, messages=PROMPT, stream=True
    )
    for event in stream:
        t = time.perf_counter() - start
        if event.type == "message_start":
            print(f"[{t:.2f}s] message_start")
        elif event.type == "content_block_start":
            print(f"[{t:.2f}s] block_start type={event.content_block.type}")
        elif event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                answer.append(event.delta.text)
            elif event.delta.type == "thinking_delta":
                thinking_chars += len(event.delta.thinking)
        elif event.type == "message_delta":
            stop_reason = event.delta.stop_reason
            usage = event.usage
        elif event.type == "message_stop":
            print(f"[{t:.2f}s] message_stop")

    print(f"\nthinking chars: {thinking_chars}")
    print(f"answer: {''.join(answer)}")
    print(f"stop_reason: {stop_reason} | usage: {usage}")


if __name__ == "__main__":
    main()
