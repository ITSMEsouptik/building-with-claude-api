"""Offline tests for graders and harness (fake runner), plus one live eval smoke test."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset import DATASET, Case
from eval_prompts import V2_SPEC
from graders import extract_json, grade_category, grade_urgency, grade_valid_format
from harness import compare, make_runner, run_eval

CASE = Case("t", "x", "billing", 4)
GOOD = '{"customer": "Ana", "category": "billing", "urgency": 4, "summary": "Double charge."}'


def test_dataset_is_well_formed() -> None:
    assert len({c.id for c in DATASET}) == len(DATASET)
    assert all(c.category in {"billing", "bug", "feature_request", "other"} and 1 <= c.urgency <= 5 for c in DATASET)


def test_extract_json_handles_tags_and_fences() -> None:
    assert extract_json(f"<json>{GOOD}</json>") == GOOD
    assert extract_json(f"```json\n{GOOD}\n```") == GOOD


def test_code_graders() -> None:
    assert grade_valid_format(CASE, GOOD).score == 1.0
    assert grade_valid_format(CASE, "nope").score == 0.0
    assert grade_category(CASE, GOOD).score == 1.0
    assert grade_category(CASE, GOOD.replace("billing", "bug")).score == 0.0
    assert grade_urgency(CASE, GOOD).score == 1.0
    assert grade_urgency(CASE, GOOD.replace("4", "5")).score == 0.5
    assert grade_urgency(CASE, GOOD.replace("4", "1")).score == 0.0


def test_harness_aggregates_and_compares() -> None:
    perfect = run_eval("perfect", lambda c: f'{{"customer": "x", "category": "{c.category}", "urgency": {c.urgency}, "summary": "s"}}')
    broken = run_eval("broken", lambda c: "garbage")
    assert perfect.overall == 1.0 and broken.overall == 0.0
    assert "regressions" in compare(perfect, broken)
    assert "regressions" not in compare(broken, perfect)


def test_live_eval_smoke() -> None:
    """Live: 3 cases through the spec prompt should mostly produce valid tickets."""
    report = run_eval("smoke", make_runner(V2_SPEC), dataset=DATASET[:3])
    assert report.by_grader()["valid_format"] >= 0.66
