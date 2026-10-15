"""Two ways to get a validated Ticket (tags + stop sequence, JSON schema) and a retry wrapper."""
import sys
from pathlib import Path
from typing import Callable, TypeVar

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, ValidationError

from common.client import chat, text_of
from prompts import EXTRACT_V2

T = TypeVar("T", bound=BaseModel)

MAX_TOKENS = 600  # generous: thinking can share this budget


class ExtractionError(Exception):
    """Raised when output could not be parsed into the model after all attempts."""


def parse_model(raw: str, model_cls: type[T]) -> T:
    """Validate raw JSON text. Raises ValidationError for bad JSON or a wrong shape."""
    return model_cls.model_validate_json(raw.strip())


def _user_turn(email: str) -> dict:
    return {"role": "user", "content": f"<email>{email}</email>"}


def _strip_fences(s: str) -> str:
    """Remove a leading ```json line and trailing ``` if the model fenced its JSON."""
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


def extract_with_tags(email: str, model_cls: type[T]) -> T:
    """Ask for JSON inside <json> tags, stop at </json>, then validate."""
    r = chat(
        [{"role": "user", "content": f"<email>{email}</email>\n\nPut the JSON inside <json></json> tags."}],
        system=EXTRACT_V2,
        max_tokens=MAX_TOKENS,
        stop_sequences=["</json>"],
    )
    if r.stop_reason == "max_tokens":
        raise ExtractionError("truncated: hit max_tokens before the JSON finished")
    text = text_of(r)
    start = text.find("<json>")
    if start == -1:
        raise ExtractionError("no <json> tag in reply")
    return parse_model(_strip_fences(text[start + len("<json>"):]), model_cls)


def extract_with_schema(email: str, model_cls: type[T]) -> T:
    """Ask the API to constrain output to the model's JSON schema, then validate."""
    r = chat(
        [_user_turn(email)],
        system=EXTRACT_V2,
        max_tokens=MAX_TOKENS,
        output_config={"format": {"type": "json_schema", "schema": model_cls.model_json_schema()}},
    )
    if r.stop_reason == "max_tokens":
        raise ExtractionError("truncated: hit max_tokens before the JSON finished")
    return parse_model(text_of(r), model_cls)


def with_retry(extractor: Callable[[str, type[T]], T], email: str, model_cls: type[T], retries: int = 1) -> T:
    """Call `extractor`; on a parse/validation failure try again, then raise ExtractionError."""
    last: Exception | None = None
    for _ in range(retries + 1):
        try:
            return extractor(email, model_cls)
        except (ValidationError, ExtractionError) as e:
            last = e
    raise ExtractionError(f"failed after {retries + 1} attempts: {last}")
