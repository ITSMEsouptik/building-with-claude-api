"""Demonstrate XML tags + a 'data not instructions' rule against a prompt-injection email."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_prompt_evals"))

from dataset import DATASET
from graders import grade_valid_format
from harness import make_runner
from variants import T0_BASELINE, T2_XML

case = next(c for c in DATASET if c.id == "tricky_ignore")
for name, system in [("t0_baseline", T0_BASELINE), ("t2_xml", T2_XML)]:
    out = make_runner(system)(case)
    print(f"{name}: valid={grade_valid_format(case, out).score}\n{out}\n")
