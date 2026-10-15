"""Run one prompt through the full eval (code graders + model-graded summary) and save results."""
import sys

from eval_prompts import V2_SPEC
from graders import CODE_GRADERS, grade_summary_model
from harness import make_runner, run_eval, save_report


def main(with_judge: bool = True) -> None:
    graders = CODE_GRADERS + ([grade_summary_model] if with_judge else [])
    report = run_eval("v2_spec", make_runner(V2_SPEC), graders=graders)
    print(report.summary())
    print("saved:", save_report(report))


if __name__ == "__main__":
    main(with_judge="--no-judge" not in sys.argv)
