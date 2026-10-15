# 05: Prompt evals

**What I learned:** an eval is dataset + runner + graders + aggregation, and its value is the *delta* between prompt versions, not the absolute number. Keeping the harness separate from the prompt makes each iteration one line of change.

**What surprised me**
- `"Output JSON."` scored 0.000, not 0.5. The model produced valid JSON with a schema it made up. Format is part of the spec.
- A "technique regression" turned out to be an empty output: thinking ate `max_tokens=400`. Always read raw outputs of the failures before believing a score.
- With 12 cases and a strong prompt, the score saturates at 0.972 and cannot rank techniques.

**Trade-offs**
- Code graders: free and deterministic, but only for checkable answers. Model graders: handle fuzzy quality but add cost, latency, and their own bias, so spot-check them against human labels.
- Partial credit (urgency off by one = 0.5) captures subjectivity but hides how many answers were exactly right. Report both.
- Bigger dataset = trustworthy deltas but more calls. Start with ~12 for iteration, grow it for decisions; use Haiku to iterate.

**Interview paragraph:** Before tuning a prompt I build a small labelled dataset that includes edge and adversarial cases, then a harness that runs the prompt, grades with code first and a model judge only where code cannot, and reports per-grader and overall scores. I change one thing per iteration and compare against the saved baseline. I inspect raw outputs of failures, because truncation, grader bugs, and format drift all look like "the prompt got worse".

## Exam-prep Q&A

- **Why evaluate prompts at all?** Prompts fail silently and unpredictably; without measurement you tune on anecdotes and ship regressions.
- **Order of grader types?** Code-based first (cheap, deterministic), model-based for fuzzy criteria, human to calibrate.
- **How do you make a model grader reliable?** Give a clear rubric, ask for reasoning before the score, constrain the output format, validate it, test against human labels, use a separate or stronger model where possible.
- **What goes in a dataset?** Representative cases, edge cases, adversarial cases (injection, empty input, ambiguous), with expected answers. Never reuse eval cases as few-shot examples.
- **Why score 0-1?** Lets different graders be averaged and compared.
- **Eval score dropped after a change. What first?** Check raw outputs and `stop_reason` for truncation or parse failures, then check whether the dataset or grader changed.
- **Where do evals sit in the workflow?** Draft prompt -> eval -> modify one thing -> re-eval -> keep if delta is real. Also rerun on every model upgrade.

**Results:** `pytest 05_prompt_evals`: 5 passed. `exercise_compare.py`: v1_bare 0.000 -> v2_spec 0.972. `example_eval.py`: overall 0.958 with judge (summary_judge 0.917). Saved reports in `05_prompt_evals/results/`.
