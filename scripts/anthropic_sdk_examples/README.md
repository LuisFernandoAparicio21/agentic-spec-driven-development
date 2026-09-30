# Anthropic SDK spec verifier

A batch/CI mode for the same harness. The interactive flow runs through
Claude Code (`.claude/agents/*`); these scripts call the Claude API
directly through the Anthropic Python SDK to review specs under `specs/`
against the harness's own rules, with no interactive session.

- `verify_spec.py` — reviews one spec (a file, or a `specs/<id>/` directory
  whose `.md` files are concatenated) and prints a JSON verdict.
- `verify_batch.py` — reviews every `specs/*/` directory in parallel and
  writes a markdown report. Exits `1` if any spec is not `APPROVED`.

```
  spec_author.md ┐
  docs/07 (SDD)  ├─▶ SYSTEM (rules, cached) ──┐
  CHECKPOINTS.md ┘                            ├─▶ Claude API ──▶ JSON verdict
  specs/<id>/*.md ───▶ USER (the spec) ───────┘                   APPROVED | CHANGES_REQUESTED
                                                                  + issues[]

  verify_batch.py:  spec #1 alone (writes cache) ──▶ specs #2..N in parallel (read cache)
                                                             │
                                             report.md + exit 1 if any spec ≠ APPROVED
```

## When to use the SDK vs Claude Code

| | Claude Code CLI | SDK (these scripts) |
|---|---|---|
| Who drives | A human, turn by turn | A script or CI job |
| Tools | Read/Edit/Bash, subagents, hooks | None: one request in, one JSON verdict out |
| Output | Conversation + files on disk | Schema-validated JSON (`output_config.format`) |
| Good for | Writing specs, implementing, reviewing with context | Re-checking many specs on every push, cheaply and repeatably |

The SDK path doesn't replace `spec_author` or `reviewer`. It's the
forced-verification idea from `METHODOLOGY.md` running without a human in
the loop: the same rules applied the same way to every spec.

## Install

```bash
cd scripts/anthropic_sdk_examples
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then set ANTHROPIC_API_KEY
```

`.env` is gitignored. `ANTHROPIC_API_KEY` already set in the environment
works too.

## Run

```bash
# One spec (a directory or a single file), JSON on stdout
python verify_spec.py ../../specs/create-task | jq '.verdict, (.issues | length)'
python verify_spec.py ../../examples/illustrative-review-cycle/01-spec.md

# Every spec under specs/, report to a file
python verify_batch.py --out report.md
```

The token usage for each call goes to stderr, so stdout stays pure JSON:

```
[../../specs/create-task] cache_read=0 cache_write=5xxx input=4xxx output=6xx
```

The default model is `claude-opus-5-5` at `effort: medium`. Pass
`--model claude-sonnet-5-5` for a cheaper run. If the model declines
the request, `fallbacks: "default"` (server-side fallback beta) re-runs it
on a fallback model inside the same call.

## Prompt caching explained

Each request has two parts:

1. **System prompt (stable, ~5k tokens):** `.claude/agents/spec_author.md`,
   `docs/07-spec-driven-development.md` and `CHECKPOINTS.md`, concatenated
   in a fixed order. It carries `cache_control: {"type": "ephemeral"}`.
2. **User turn (changes each time):** the spec being reviewed.

Caching is a prefix match, so everything up to the breakpoint is cached,
and the only part that changes sits after it. The first call writes the
cache (`cache_creation_input_tokens > 0`, billed at 1.25x input). Every
call within the next 5 minutes reads it instead
(`cache_read_input_tokens > 0`). On Opus 5.5 a read costs $0.20/MTok,
against $4/MTok for uncached input. The cached prefix is therefore about 95%
cheaper on each call after the first, and it's processed faster.

To see it, run the same command twice:

```bash
python verify_spec.py ../../specs/create-task > /dev/null   # cache_write>0, cache_read=0
python verify_spec.py ../../specs/create-task > /dev/null   # cache_read>0
```

Three details the code relies on:

- **Stay above the minimum.** Prefixes shorter than the model's minimum
  (512 tokens on Opus 5.5 / Sonnet 5.5) never cache, and no error is raised.
  The rules files are well above it.
- **Keep the prefix byte-stable.** Don't add a timestamp, the spec name, or
  anything else that varies to the system prompt. `RULE_FILES` has a fixed
  order for the same reason. Editing a rules file invalidates the cache
  once, and that's correct.
- **Warm the cache before going parallel.** A cache entry exists only once
  the first response starts. Four cold calls fired at the same time would
  all miss and all pay the write. `verify_batch.py` runs the first spec
  alone and then sends the rest through the thread pool, so every parallel
  call reads the cache.

## Integration with the harness

To gate CI, add a job that runs `verify_batch.py --out report.md` whenever
`specs/**` changes and uploads the report. The exit code fails the job when
a spec isn't `APPROVED`.

As an optional local hook, a `Stop` hook in `.claude/settings.json` could run
`python scripts/anthropic_sdk_examples/verify_batch.py` next to `./init.sh`.
It's left out of the default settings because every session close would
then cost API calls. Turn it on per project if you want it.

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

- `tests/test_offline.py` needs no API key. A fake client records every
  request and checks the parts caching depends on: the system prompt is
  byte-identical across calls and carries `cache_control`, only the user
  turn changes, and the structured output schema is sent. It also checks
  that stdout is pure JSON with usage on stderr, that API errors exit with
  `2`, and that the batch warms the cache with the first spec before the
  parallel pool and exits `1` on any non-`APPROVED` spec.
- `tests/test_live_cache.py` makes two real calls and asserts that the
  second one has `cache_read_input_tokens > 0`. It is skipped when
  `ANTHROPIC_API_KEY` is not set (in the environment or `.env`).
