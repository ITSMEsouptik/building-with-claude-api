"""Live smoke test (makes one tiny real API call)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of


def test_basic_response() -> None:
    """A short prompt returns text and ends naturally."""
    response = chat([{"role": "user", "content": "Say hi."}], max_tokens=50)
    assert text_of(response).strip()
    assert response.stop_reason == "end_turn"
    assert response.usage.output_tokens > 0
