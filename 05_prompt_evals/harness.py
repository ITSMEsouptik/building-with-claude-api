"""Reusable eval harness: dataset -> run prompt -> grade -> aggregate -> save.

Change one thing per iteration (the prompt), keep dataset and graders fixed, and
compare the aggregate scores. Results are saved as JSON so deltas can be tracked.
"""
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.client import chat, text_of
from dataset import DATASET, Case
from graders import CODE_GRADERS, Grade, Grader

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# A runner turns a case into raw model output. Swappable, so tests can fake it.
Runner = Callable[[Case], str]


@dataclass
class CaseResult:
    case_id: str
    output: str
    grades: list[Grade]

    @property
    def score(self) -> float:
        return sum(g.score for g in self.grades) / len(self.grades) if self.grades else 0.0


@dataclass
class EvalReport:
    name: str
    results: list[CaseResult] = field(default_factory=list)

    def by_grader(self) -> dict[str, float]:
        """Mean score per grader across all cases."""
        totals: dict[str, list[float]] = {}
        for r in self.results:
            for g in r.grades:
                totals.setdefault(g.name, []).append(g.score)
        return {k: sum(v) / len(v) for k, v in totals.items()}

    @property
    def overall(self) -> float:
        """Mean of the per-case scores."""
        return sum(r.score for r in self.results) / len(self.results) if self.results else 0.0

    def summary(self) -> str:
        lines = [f"{self.name}: overall {self.overall:.3f} over {len(self.results)} cases"]
        lines += [f"  {k:<15} {v:.3f}" for k, v in self.by_grader().items()]
        return "\n".join(lines)


def make_runner(system: str, *, model: str | None = None, max_tokens: int = 1500, user_template: str = "<email>{email}</email>") -> Runner:
    """Build a runner that sends one case through `system` with the email in the user turn."""

    def run(case: Case) -> str:
        kwargs = {"model": model} if model else {}
        r = chat([{"role": "user", "content": user_template.format(email=case.email)}], system=system, max_tokens=max_tokens, **kwargs)
        return text_of(r)

    return run


def run_eval(name: str, runner: Runner, dataset: list[Case] = DATASET, graders: list[Grader] = CODE_GRADERS) -> EvalReport:
    """Run every case through `runner`, apply every grader, return the report."""
    report = EvalReport(name)
    for case in dataset:
        output = runner(case)
        report.results.append(CaseResult(case.id, output, [g(case, output) for g in graders]))
    return report


def save_report(report: EvalReport) -> Path:
    """Write the report (including raw outputs) to results/<name>-<timestamp>.json."""
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{report.name}-{int(time.time())}.json"
    path.write_text(json.dumps({"overall": report.overall, "by_grader": report.by_grader(), "results": [asdict(r) for r in report.results]}, indent=2))
    return path


def compare(baseline: EvalReport, candidate: EvalReport) -> str:
    """Show per-grader and overall score deltas, and cases that got worse."""
    b, c = baseline.by_grader(), candidate.by_grader()
    lines = [f"{baseline.name} -> {candidate.name}", f"  overall {baseline.overall:.3f} -> {candidate.overall:.3f} ({candidate.overall - baseline.overall:+.3f})"]
    lines += [f"  {k:<15} {b[k]:.3f} -> {c[k]:.3f} ({c[k] - b[k]:+.3f})" for k in b if k in c]
    base_scores = {r.case_id: r.score for r in baseline.results}
    worse = [r.case_id for r in candidate.results if r.score < base_scores.get(r.case_id, 0)]
    if worse:
        lines.append(f"  regressions: {', '.join(worse)}")
    return "\n".join(lines)
