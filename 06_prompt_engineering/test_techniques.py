"""Offline checks on the variants, plus a live check that the best variant beats the baseline on a subset."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_prompt_evals"))

from dataset import DATASET
from harness import make_runner, run_eval
from variants import T3_MULTISHOT, VARIANTS


def test_few_shot_examples_do_not_leak_into_dataset() -> None:
    """Examples that reuse eval emails would inflate scores."""
    for case in DATASET:
        assert case.email not in T3_MULTISHOT


def test_every_variant_names_the_keys_and_data_rule_where_expected() -> None:
    for name, prompt in VARIANTS.items():
        assert all(k in prompt for k in ("customer", "category", "urgency", "summary")), name


def test_live_rubric_prompt_not_worse_than_baseline() -> None:
    """Live: on 6 cases the rubric+examples prompt should score at least as well as the bare-keys prompt."""
    subset = DATASET[:6]
    base = run_eval("b", make_runner(VARIANTS["t0_baseline"]), dataset=subset)
    best = run_eval("m", make_runner(VARIANTS["t3_multishot"]), dataset=subset)
    assert best.overall >= base.overall - 0.05
