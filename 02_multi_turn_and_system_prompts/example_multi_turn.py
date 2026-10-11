"""
Example of a multi-turn conversation with system prompts.
The API is stateless, so the full conversation history must be sent each time.
"""

from pyexpat.errors import messages
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of

def main() -> None:
    """ Run a 3-turn conversation and show that turn 3 depends on turn 1. """
    messages: list[dict] = []
    for user_text in [
        "My name is Souptik and I'm learning the Claude API.",
        "What's a good first project ?",
        "What's my name and what am I learning ?", # only answerable via history
    ]:
        messages.append({"role": "user", "content": user_text})
        response = chat(messages, max_tokens=200)
        reply = text_of(response)
        messages.append({"role": "assistant", "content": reply})
        print(f"User: {user_text}\nClaude: {reply}\n")

    print(f"messages sent on the last call: {len(messages) - 1}")

if __name__ == "__main__":
    main()