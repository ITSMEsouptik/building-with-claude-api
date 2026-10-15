"""Score every prompt variant on the same dataset and graders; print the table and step-by-step deltas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_prompt_evals"))

from harness import compare, make_runner, run_eval, save_report
from variants import VARIANTS


def main() -> None:
    reports = []
    for name, system in VARIANTS.items():
        report = run_eval(name, make_runner(system))
        save_report(report)
        reports.append(report)
    print(f"{'variant':<14}{'overall':>8}{'format':>8}{'category':>10}{'urgency':>9}")
    for r in reports:
        g = r.by_grader()
        print(f"{r.name:<14}{r.overall:>8.3f}{g['valid_format']:>8.3f}{g['category']:>10.3f}{g['urgency']:>9.3f}")
    print()
    for prev, cur in zip(reports, reports[1:]):
        print(compare(prev, cur), "\n")


if __name__ == "__main__":
    main()
