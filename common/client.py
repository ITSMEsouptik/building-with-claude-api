"""Shared Anthropic client setup, a chat helper with retries, and usage logging."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

# Make `import config` work when scripts run from a topic subfolder.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config  # noqa: E402

load_dotenv(ROOT / ".env")

logger = logging.getLogger("claude_course")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# The SDK retries 429, 5xx (incl. 529 overloaded), connection errors and
# timeouts with exponential backoff. Configure it here, not ad hoc per script.
MAX_RETRIES = 5
TIMEOUT_SECONDS = 60.0

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Return a shared Anthropic client (reads ANTHROPIC_API_KEY from env/.env)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=MAX_RETRIES, timeout=TIMEOUT_SECONDS)
    return _client


def log_usage(response: anthropic.types.Message, label: str = "") -> dict[str, int]:
    """Log token usage for a response. Returns a dict of the token counts."""
    u = response.usage
    usage = {
        "input_tokens": u.input_tokens,
        "output_tokens": u.output_tokens,
        "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
    }
    logger.info("usage %s model=%s %s", label, response.model, usage)
    return usage


def chat(
    messages: list[dict[str, Any]],
    *,
    system: str | None = None,
    model: str = config.DEFAULT_MODEL,
    max_tokens: int = config.DEFAULT_MAX_TOKENS,
    **kwargs: Any,
) -> anthropic.types.Message:
    """Send one request to the Messages API and log usage.

    The API is stateless: `messages` must hold the full history. Extra kwargs
    (stop_sequences, tools, ...) pass straight through.
    Returns the full Message object so callers can inspect stop_reason, etc.
    """
    params: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "messages": messages, **kwargs}
    if system is not None:
        params["system"] = system
    try:
        response = get_client().messages.create(**params)
    except anthropic.RateLimitError:
        logger.error("Rate limited (429) after %d retries", MAX_RETRIES)
        raise
    except anthropic.APITimeoutError:
        logger.error("Timed out after %.0fs x %d retries", TIMEOUT_SECONDS, MAX_RETRIES)
        raise
    except anthropic.APIStatusError as e:
        # 529 = overloaded; 401 = bad key; 404 = bad model id.
        logger.error("API error %s: %s", e.status_code, e.message)
        raise
    log_usage(response)
    if response.stop_reason == "max_tokens":
        logger.warning(
            "Hit max_tokens=%d; thinking and text share this budget, so output may be truncated or empty",
            max_tokens,
        )
    return response

def stream_chat(
    messages: list[dict[str, Any]],
    *,
    system: str | None = None,
    model: str = config.DEFAULT_MODEL,
    max_tokens: int = config.DEFAULT_MAX_TOKENS,
    **kwargs: Any,
):
    """Open an SDK streaming context. Use as `with stream_chat(...) as stream:`.

    Iterate `stream.text_stream` for text, then call `stream.get_final_message()`
    to get the full Message (and its usage) once the stream ends.
    """
    params: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "messages": messages, **kwargs}
    if system is not None:
        params["system"] = system
    return get_client().messages.stream(**params)



def text_of(response: anthropic.types.Message) -> str:
    """Concatenate the text blocks of a response."""
    return "".join(b.text for b in response.content if b.type == "text")
