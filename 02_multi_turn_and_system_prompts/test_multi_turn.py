"""Unit tests (no API) for trimming, plus one live test showing history is what gives memory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of
from exercise_history import trim_history


def _history(n_pairs: int) -> list[dict]:
    msgs: list[dict] = []
    for i in range(n_pairs):
        msgs += [{"role": "user", "content": f"q{i}"}, {"role": "assistant", "content": f"a{i}"}]
    return msgs


def test_trim_keeps_last_pairs_and_starts_with_user() -> None:
    out = trim_history(_history(5), max_turns=2)
    assert len(out) == 4
    assert out[0] == {"role": "user", "content": "q3"}


def test_trim_short_history_unchanged() -> None:
    assert trim_history(_history(1), max_turns=3) == _history(1)


def test_history_is_what_gives_memory() -> None:
    """Live: with history Claude knows the codeword; without it, it cannot."""
    with_history = [
        {"role": "user", "content": "The codeword is PINEAPPLE. Just say OK."},
        {"role": "assistant", "content": "OK"},
        {"role": "user", "content": "What is the codeword? One word."},
    ]
    without = [with_history[-1]]
    ans_with = text_of(chat(with_history, max_tokens=300)).upper()
    ans_without = text_of(chat(without, max_tokens=300)).upper()
    assert ans_with.strip(), "empty reply: thinking may have used the whole max_tokens"
    assert "PINEAPPLE" in ans_with
    assert ans_without.strip()
    assert "PINEAPPLE" not in ans_without
