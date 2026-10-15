"""Offline tests for parsing and validation, plus live tests that skip if a route is unsupported."""
import sys
from pathlib import Path

import anthropic
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from common.client import chat
from extract import ExtractionError, extract_with_schema, extract_with_tags, parse_model, with_retry
from schemas import Ticket

GOOD = '{"customer": "Ana", "category": "billing", "urgency": 4, "summary": "Double charge."}'
EMAIL = "Hi, this is Ana Ruiz. I was charged twice for May and need it fixed today, please."


def test_parse_valid_json() -> None:
    assert parse_model(GOOD, Ticket).category == "billing"


def test_parse_rejects_invalid_json() -> None:
    with pytest.raises(ValidationError):
        parse_model("not json", Ticket)


def test_parse_rejects_bad_enum_and_range() -> None:
    with pytest.raises(ValidationError):
        parse_model(GOOD.replace("billing", "refund"), Ticket)
    with pytest.raises(ValidationError):
        parse_model(GOOD.replace("4", "9"), Ticket)


def test_parse_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        parse_model(GOOD[:-1] + ', "extra": 1}', Ticket)


def test_retry_recovers_then_gives_up() -> None:
    calls = {"n": 0}

    def flaky(email: str, cls):
        calls["n"] += 1
        if calls["n"] == 1:
            return parse_model("oops", cls)
        return parse_model(GOOD, cls)

    assert with_retry(flaky, EMAIL, Ticket).customer == "Ana"
    with pytest.raises(ExtractionError):
        with_retry(lambda e, c: parse_model("oops", c), EMAIL, Ticket)


@pytest.mark.parametrize("extractor", [extract_with_tags, extract_with_schema])
def test_live_extraction(extractor) -> None:
    """Live: skip (not fail) if the API rejects this route for the model."""
    try:
        ticket = with_retry(extractor, EMAIL, Ticket)
    except anthropic.BadRequestError as e:
        pytest.skip(f"{extractor.__name__} rejected by API: {e.message}")
    assert ticket.category == "billing"
    assert 1 <= ticket.urgency <= 5


def test_prefill_is_rejected_by_this_model() -> None:
    """Documents current behaviour: Haiku 5.5 rejects an assistant prefill with a 400."""
    with pytest.raises(anthropic.BadRequestError):
        chat(
            [{"role": "user", "content": "Return JSON."}, {"role": "assistant", "content": "{"}],
            max_tokens=50,
        )
