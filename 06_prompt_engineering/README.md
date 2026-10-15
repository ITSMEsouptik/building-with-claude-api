# Lesson 06: Prompt engineering

**What it is:** shaping the prompt so the model reliably does what you meant. Treated as an experiment: every technique is scored with the lesson 05 harness, one change at a time.

**When to use:** after you have an eval. Without one you cannot tell whether a technique helped.

## Techniques

| Technique | What to do | Why it works |
|-----------|-----------|--------------|
| Be clear and direct | State the task first, use imperative verbs, say what the output is for | The model cannot read intent; ambiguity gets filled with guesses |
| Specify output format | Name keys, types, allowed values; say "no prose, no fences" | Downstream code needs a stable shape |
| Define terms and rubrics | Say what each category and each urgency level means | Subjective labels are the main source of error |
| XML tags | Wrap data (`<email>`) and sections (`<rules>`) | Unambiguous boundaries; also separates data from instructions |
| Multishot (examples) | 2-5 input/output pairs in `<examples>` | Shows format and judgement calibration better than describing it |
| Prefill | Start the assistant turn | **Rejected (400) on Haiku 5.5**; use tags + stop sequence or JSON schema |
| Role / system prompt | One line of persona or context in `system` | Sets tone and domain; weakest of the set for extraction |
| Let it think | Reasoning before answer | Helps multi-step tasks; costs tokens and latency |

## Files

| File | Purpose |
|------|---------|
| `variants.py` | `T0_BASELINE`, `T1_CLEAR`, `T2_XML`, `T3_MULTISHOT`, one technique added per step |
| `exercise_ladder.py` | scores all variants on the lesson 05 dataset, prints a table and step deltas |
| `example_xml_injection.py` | prompt-injection email against baseline vs XML prompt |
| `test_techniques.py` | no-leakage check, key check, live "not worse than baseline" check |

```bash
python 06_prompt_engineering/exercise_ladder.py   # ~48 haiku calls
pytest 06_prompt_engineering
```

## Results (claude-haiku-5-5, same 12 cases and graders as lesson 05)

| Variant | overall | valid_format | category | urgency |
|---------|---------|--------------|----------|---------|
| `t0_baseline` (keys only) | 0.000 | 0.000 | 0.000 | 0.000 |
| `t1_clear` (+ definitions, rubric) | 0.972 | 1.000 | 1.000 | 0.917 |
| `t2_xml` (same content in tags) | 0.972 | 1.000 | 1.000 | 0.917 |
| `t3_multishot` (+ 3 examples) | 0.972 | 1.000 | 1.000 | 0.917 |

**Honest reading:**
- The big jump is baseline -> clear: listing keys was not enough. The model returned `urgency: "high"` and categories like `"General"`. Defining the values fixed it.
- t1, t2, t3 are tied. The remaining misses are off-by-one urgency on subjective cases (`other_partner`, `billing_fraud`, `tricky_ignore`). At 12 cases that is noise. **I cannot claim XML or examples helped here;** the dataset is too small and too easy to separate them. Next step would be 50+ cases including hard ones.
- Injection demo (`example_xml_injection.py`, single run, anecdotal): baseline produced an invalid ticket (`urgency: "medium"`) and mentioned the injected instruction inside the summary; the XML prompt with the "email is data" rule gave a valid ticket.
- An earlier run at `max_tokens=400` showed t2 "regressing" to 0.806. The cause was an empty output from truncation, not the technique. Fixed by raising the harness default to 1500.

## Common mistakes

- Adding several techniques at once, then crediting the wrong one.
- Examples that duplicate eval cases (inflates score). Tested for in `test_techniques.py`.
- Examples that are all the same label, which biases the output toward it.
- Vague quality words ("be concise", "be accurate") instead of testable constraints.
- Relying on prefill. It is not portable across models.
- Putting untrusted text outside tags, or without saying it is data.
