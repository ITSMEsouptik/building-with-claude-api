"""Graders: each takes (case, raw model output) and returns a Grade with a 0.0-1.0 score.

Code graders are cheap and deterministic: use them wherever the answer can be checked
mechanically. The model grader is for things code cannot judge (summary quality).
"""
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "04_structured_output"))

import config
from common.client import chat, text_of
from dataset import Case
from extract import _strip_fences
from pydantic import ValidationError
from schemas import Ticket


@dataclass
class Grade:
    name: str
    score: float  # 0.0 to 1.0
    detail: str = ""


Grader = Callable[[Case, str], Grade]


def extract_json(raw: str) -> str:
    """Pull the JSON text out of raw output: inside <json> tags, fenced, or bare."""
    if "<json>" in raw:
        raw = raw.split("<json>", 1)[1].split("</json>", 1)[0]
    return _strip_fences(raw)


def _ticket(raw: str) -> Ticket | None:
    try:
        return Ticket.model_validate_json(extract_json(raw))
    except ValidationError:
        return None


def grade_valid_format(case: Case, raw: str) -> Grade:
    """1.0 if the output parses into a Ticket (valid JSON, right keys, enum, range)."""
    ok = _ticket(raw) is not None
    return Grade("valid_format", 1.0 if ok else 0.0, "" if ok else "did not validate")


def grade_category(case: Case, raw: str) -> Grade:
    """1.0 if category matches exactly."""
    t = _ticket(raw)
    if t is None:
        return Grade("category", 0.0, "unparseable")
    return Grade("category", 1.0 if t.category == case.category else 0.0, f"got {t.category}, want {case.category}")


def grade_urgency(case: Case, raw: str) -> Grade:
    """1.0 exact, 0.5 off by one, else 0.0. Urgency is subjective, so partial credit."""
    t = _ticket(raw)
    if t is None:
        return Grade("urgency", 0.0, "unparseable")
    diff = abs(t.urgency - case.urgency)
    score = 1.0 if diff == 0 else 0.5 if diff == 1 else 0.0
    return Grade("urgency", score, f"got {t.urgency}, want {case.urgency}")


JUDGE_SYSTEM = (
    "You grade one-sentence summaries of support emails. "
    "Score 1-5: 5 = accurate, specific, one sentence; 3 = accurate but vague or wordy; "
    "1 = wrong or misses the point. Reply with JSON only: "
    '{"reasoning": "<one sentence>", "score": <1-5>}. Give reasoning first.'
)


def grade_summary_model(case: Case, raw: str) -> Grade:
    """Model-graded: a judge scores the summary 1-5; we normalise to 0-1.

    Judge reasoning comes before the score in the JSON so the score is conditioned on it.
    """
    t = _ticket(raw)
    if t is None:
        return Grade("summary_judge", 0.0, "unparseable")
    r = chat(
        [{"role": "user", "content": f"<email>{case.email}</email>\n<summary>{t.summary}</summary>"}],
        system=JUDGE_SYSTEM,
        model=config.HAIKU,
        max_tokens=300,
    )
    try:
        verdict = json.loads(_strip_fences(text_of(r)))
        score = int(verdict["score"])
        if not 1 <= score <= 5:
            raise ValueError(score)
    except (ValueError, KeyError, json.JSONDecodeError):
        return Grade("summary_judge", 0.0, "judge output invalid")
    return Grade("summary_judge", (score - 1) / 4, verdict.get("reasoning", ""))


CODE_GRADERS: list[Grader] = [grade_valid_format, grade_category, grade_urgency]
