"""Iteration loop: change ONE thing (bare prompt -> spec prompt), same dataset and graders, report the delta."""
from eval_prompts import V1_BARE, V2_SPEC
from harness import compare, make_runner, run_eval, save_report


def main() -> None:
    base = run_eval("v1_bare", make_runner(V1_BARE))
    cand = run_eval("v2_spec", make_runner(V2_SPEC))
    for r in (base, cand):
        print(r.summary(), "\n")
        save_report(r)
    print(compare(base, cand))


if __name__ == "__main__":
    main()
