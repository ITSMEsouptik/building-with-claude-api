"""Live tests: streaming matches non-streaming content, and stop_sequences actually stop."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, stream_chat, text_of

PROMPT = [{"role": "user", "content": "Reply with exactly the word: ready"}]


def test_stream_text_equals_final_message_text() -> None:
    with stream_chat(PROMPT, max_tokens=300) as stream:
        chunks = list(stream.text_stream)
        final = stream.get_final_message()
    assert "".join(chunks) == text_of(final)
    assert final.stop_reason == "end_turn"


def test_stop_sequence_halts_generation() -> None:
    r = chat(
        [{"role": "user", "content": "Count from 1 to 10, one number per line."}],
        max_tokens=300,
        stop_sequences=["5"],
    )
    assert r.stop_reason == "stop_sequence"
    assert r.stop_sequence == "5"
    assert "5" not in text_of(r)


def test_low_max_tokens_reports_max_tokens() -> None:
    r = chat(
        [{"role": "user", "content": "Write a 500-word essay about the sea."}],
        max_tokens=30,
    )
    assert r.stop_reason == "max_tokens"
