"""Minimal first call: one user message in, one reply out, usage logged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of


def main() -> None:
    """Send a single message and print the reply and stop reason."""
    response = chat(
        [{"role": "user", "content": "In one sentence, what is an API?"}],
        max_tokens=100,
    )
    print(text_of(response))
    print("stop_reason:", response.stop_reason)


if __name__ == "__main__":
    main()
