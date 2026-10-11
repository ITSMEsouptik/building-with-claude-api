"""Chatbot with a bounded history window. Keeps input cost flat as conversations grow."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of
from prompts import TUTOR_V2


def trim_history(messages: list[dict], max_turns: int) -> list[dict]:
    """Keep the last `max_turns` user/assistant pairs. Returns a list starting on a user message."""
    trimmed = messages[-(max_turns * 2):]
    while trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]
    return trimmed


class Conversation:
    """Holds an explicit, inspectable message list and sends a trimmed window each call."""

    def __init__(self, system: str, max_turns: int = 4) -> None:
        self.system = system
        self.max_turns = max_turns
        self.messages: list[dict] = []

    def send(self, user_text: str) -> str:
        """Add a user turn, call the API with the window, store and return the reply text."""
        self.messages.append({"role": "user", "content": user_text})
        window = trim_history(self.messages, self.max_turns)
        response = chat(window, system=self.system, max_tokens=300)
        reply = text_of(response)
        self.messages.append({"role": "assistant", "content": reply})
        return reply


if __name__ == "__main__":
    convo = Conversation(TUTOR_V2, max_turns=2)
    for q in [
        "My favourite colour is teal.",
        "What is a list?",
        "What is a dict?",
        "What's my favourite colour?",  # teal has fallen out of the 2-turn window
    ]:
        print(f"USER: {q}\nCLAUDE: {convo.send(q)}\n")
