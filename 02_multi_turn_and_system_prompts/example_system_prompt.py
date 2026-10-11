""" Show the effect of a system prompt, side by side. """
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of
from prompts import TUTOR_V1, TUTOR_V2

QUESTION = [{"role": "user", "content": "What is a Python decorator ?"}]

def main() -> None:
    for name, system in [("V1", TUTOR_V1), ("V2", TUTOR_V2)]:
        print(f"=== {name} ===")
        response = chat(QUESTION, system=system, max_tokens=200)
        print(text_of(response))
        print("stop_reason:", response.stop_reason)
        print()


if __name__ == "__main__":
    main()