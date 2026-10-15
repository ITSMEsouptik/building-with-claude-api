# Building with the Claude API: course workspace

A hands-on companion to the "Building with the Claude API" course. Each lesson has runnable code, tests, and a short note on what I learned and why the design is the way it is.

## Setup

Requires Python 3.11+.

```bash
cd "/Volumes/Crucial X6/learning/claude-certified-architect-foundation/building with claude api"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your real key in .env
```

Set `ANTHROPIC_API_KEY` in `.env`. Never commit `.env`; it is listed in `.gitignore`.

## Layout

```
config.py          model IDs and shared defaults (change models here)
common/client.py   shared client, chat() helper with retries, usage logging
01_api_basics/     first call, smoke test
02_multi_turn_and_system_prompts/
03_streaming_and_params/
...                one folder per lesson, numbered in course order
notes/             one note per lesson
```

## Running things

```bash
python 01_api_basics/example_hello.py     # one live call
pytest 01_api_basics                      # live smoke test
pytest 02_multi_turn_and_system_prompts   # unit tests and live checks
pytest 05_prompt_evals 06_prompt_engineering   # eval harness + technique ladder
```

Tests that call the API cost a small amount each run. Keep `max_tokens` low and avoid loops without a cost estimate.

## Models

Set in `config.py`:

| Role | Model ID | Use |
|------|----------|-----|
| Default | `claude-haiku-5-5` | iteration, evals |
| Step up | `claude-sonnet-5-5` | when quality matters |
| Hard reasoning | `claude-opus-5-5` | hardest problems |

Check model IDs against https://docs.claude.com before relying on them.

## Progress

| Lesson | Code | Tests | Note | Status |
|--------|------|-------|------|--------|
| 01 API basics | written | written, not yet run | pending | in progress |
| 02 Multi-turn and system prompts | written | written, not yet run | pending | in progress |
| 03 Streaming and params | | | | not started |
| 04 Structured output | | | | not started |
| 05 Prompt evals | written | 5 passed | done | done |
| 06 Prompt engineering | written | 3 passed | done | done |
| 07 Tool use | | | | not started |
| 08 RAG | | | | not started |
| 09 Extended thinking | | | | not started |
| 10 Vision and PDF | | | | not started |
| 11 Citations | | | | not started |
| 12 Prompt caching | | | | not started |
| 13 Files API and code execution | | | | not started |
| 14 MCP | | | | not started |
| 15 Agents and workflows | | | | not started |
| Capstone | | | | not started |

A lesson counts as done only when it has runnable code, passing tests or logged eval output, and a note.

## Known issues

- **Temperature is not used.** `anthropic` 1.13.0 has no `temperature` argument, and newer models may reject it. Variety comes from prompting instead.
- Lesson 02 examples have not been run since the temperature fix.

## Notes

Lesson notes live in `notes/`. Each covers what I learned, what surprised me, trade-offs, and an interview-style explanation.
