"""Probe: does this model accept an assistant prefill, and does output_config.format work?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic
from common.client import chat, text_of

ASK = "Return a JSON object with keys name and age for a person called Ana, aged 31."


def try_call(label: str, **kwargs) -> None:
    """Make one capped call and print whether the API accepted it."""
    try:
        r = chat(max_tokens=300, **kwargs)
        print(f"[{label}] OK stop={r.stop_reason}\n{text_of(r)}\n")
    except anthropic.APIStatusError as e:
        print(f"[{label}] REJECTED {e.status_code}: {e.message}\n")


try_call("prefill", messages=[
    {"role": "user", "content": ASK},
    {"role": "assistant", "content": "{"},
])

try_call("json_schema", messages=[{"role": "user", "content": ASK}], output_config={
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name", "age"],
            "additionalProperties": False,
        },
    }
})
