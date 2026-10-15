# Lesson 05: Prompt evals

**What it is:** a repeatable way to measure whether a prompt change made things better. Dataset in, prompt run, grades out, one aggregate score.

**When to use:** before and after every prompt change; before swapping models; before shipping. "It looked fine on three examples" is not an eval.

## The loop

```
dataset (cases + expected answers)
   -> runner (prompt + model -> raw output)
   -> graders (code-based, model-based) -> 0..1 score per case
   -> aggregate (mean per grader, overall) -> save JSON
   -> change ONE thing, rerun, compare deltas
```

## Files

| File | Purpose |
|------|---------|
| `dataset.py` | 12 support emails with expected category and urgency |
| `graders.py` | `valid_format`, `category`, `urgency` (code); `summary_judge` (model-graded) |
| `harness.py` | `run_eval`, `make_runner`, `EvalReport`, `save_report`, `compare` |
| `eval_prompts.py` | versioned prompts under test (`V1_BARE`, `V2_SPEC`) |
| `example_eval.py` | one prompt, all graders including the judge |
| `exercise_compare.py` | v1 vs v2, prints the delta |
| `test_evals.py` | offline tests (fake runner) plus one live smoke test |
| `results/` | saved JSON reports with raw outputs |

```bash
python 05_prompt_evals/example_eval.py --no-judge   # skip the judge to save calls
python 05_prompt_evals/exercise_compare.py
pytest 05_prompt_evals
```

## Grader types

| Type | Use when | Cost | Weakness |
|------|----------|------|----------|
| Code | answer is checkable (enum, number, schema, regex) | free, deterministic | cannot judge quality or tone |
| Model | quality is fuzzy (summary, helpfulness) | extra API call | biased, noisy, needs its own checking |
| Human | calibrating the other two | slow, expensive | does not scale |

Design rules I followed:
- Score 0-1 so graders combine. Partial credit where the label is subjective (urgency off by one = 0.5).
- Judge writes its reasoning first, then the score, so the score is conditioned on the reasoning.
- Judge is told the rubric and the output format; it returns JSON that is itself validated.
- Dataset includes an adversarial case (`tricky_ignore`: prompt injection inside the email).

## Results (claude-haiku-5-5, 12 cases)

| Prompt | overall | valid_format | category | urgency |
|--------|---------|--------------|----------|---------|
| `v1_bare` ("Output JSON.") | 0.000 | 0.000 | 0.000 | 0.000 |
| `v2_spec` (keys, enums, range) | 0.972 | 1.000 | 1.000 | 0.917 |
| `v2_spec` + judge | 0.958 | 1.000 | 1.000 | 0.917 (summary_judge 0.917) |

`v1_bare` scored zero because the model invented its own schema (`ticket.customer_name`, `priority: "high"`). Not a bug in the grader: the output really was unusable by a program.

## Common mistakes

- Judging on too few cases, or a dataset that only has easy cases (saturates at ~1.0 and stops discriminating).
- Changing prompt and dataset and grader at once, so the delta cannot be attributed.
- Truncated outputs counted as model failures. **I hit this:** `max_tokens=400` returned an empty string for one case because thinking shared the budget, which looked like a technique regression. Always inspect raw outputs of failures, and log `stop_reason`.
- Grader coupling: `category` and `urgency` score 0 if the whole ticket fails validation, so one format error is counted three times. Fine for a headline number, misleading for diagnosis.
- Trusting a model grader without spot-checking it against human labels.
- Leaking eval cases into few-shot examples.

## Known limits

12 cases is a demo. A one-case change moves the overall score by about 0.08. Treat differences smaller than that as noise.
