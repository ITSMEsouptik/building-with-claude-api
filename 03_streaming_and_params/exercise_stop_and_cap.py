"""Use stop_sequences and max_tokens to control where a reply ends."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of


def first_item(question: str) -> str:
    """Ask for a numbered list but stop before item 2, so we only pay for item 1."""
    r = chat(
        [{"role": "user", "content": question}],
        system="Answer with a numbered list, starting each item on a new line as '1.', '2.', and so on.",
        max_tokens=400,
        stop_sequences=["\n2."],
    )
    print("stop_reason:", r.stop_reason, "| stop_sequence:", repr(r.stop_sequence))
    return text_of(r)


if __name__ == "__main__":
    print(first_item("Give me three tips for writing clear Python code."))
