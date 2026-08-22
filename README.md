# Agentic Spec-Driven Development for API Engineering

A documented, field-tested methodology for building REST APIs with an AI coding
agent as an active collaborator — not autocomplete, not vibe-coding. Every
endpoint goes through the same loop: **Plan → Implement → Verify → Multi-Agent
Review → Simplify → Human Approval → Ship.**

This is not a generic software methodology. It is specialized for the shape of
work that dominates backend API engineering: a request comes in as a route, a
validator decides if it's well-formed, a controller talks to the database, and
a response goes out. That specificity is what makes it fast to apply and easy
to verify — every phase below is described in terms of routes, validators,
controllers, and real HTTP requests against a real database, not abstract
"tasks."

## Why this exists

[GitHub Spec Kit](https://github.com/github/spec-kit) (128k★) proved that
spec-driven development — writing the plan as a reviewable artifact before any
code exists — works at general-purpose scale. This repo takes the same core
idea and narrows it to one domain: **API endpoint development**, where the
"spec" is a request/response contract, the "verification" is a real HTTP call
against a real database, and the "review" is a swarm of specialized agents
checking the diff from different angles before a human ever has to.

The methodology documented here was developed and used in production across
dozens of merged pull requests on a real Express + Sequelize backend. See
[`case-study/session-metrics.md`](case-study/session-metrics.md) for
anonymized numbers.

**No source code, business logic, or proprietary data from that project
appears anywhere in this repo.** Everything here — templates, examples, and
the case study — is generic and illustrative.

## Validated stack

The **methodology** (the loop, the principles, the review/verify/learn
stages) is stack-agnostic by design — nothing about it assumes a specific
language or framework. The **templates and examples in this repo**,
however, reflect the one stack this was actually developed and proven
against, and are honest about that rather than pretending to a genericity
that was never tested:

- **Runtime / framework:** Node.js + Express 4
- **Validation:** Joi
- **ORM / database:** Sequelize (SQL Server via `tedious`, though the
  pattern is equally applicable to any Sequelize-supported database)
- **Architecture:** the three-layer routes → validators → controllers split
  described in [`templates/PROJECT-CONVENTIONS.md.template`](templates/PROJECT-CONVENTIONS.md.template)

**Adapting this to a different stack** (Python + FastAPI + Pydantic, Go, a
different ORM, a different validation library) means rewriting
`PROJECT-CONVENTIONS.md.template` and the example code in
`examples/illustrative-review-cycle/` for that stack's idioms — the
workflow stages, the review lenses, and the verification discipline in
`METHODOLOGY.md` and `docs/` carry over unchanged, because none of them are
written in terms of Express, Joi, or Sequelize specifically.

## Start here

- [`METHODOLOGY.md`](METHODOLOGY.md) — the full methodology: why it works, the
  workflow in practice, core principles, and the non-negotiable guardrails.
- [`AGENTS.md`](AGENTS.md) — the entry point for an agent operating *in*
  this repo: who does what, where state lives, where the rules live. This is
  the harness itself, not a description of one — see below.
- [`docs/`](docs) — one deep-dive per phase, including
  [`06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md)
  — the "PR gets sent back → fix it → decide if it's a durable rule" cycle,
  one of the most common and easiest-to-skip stages in practice.
- [`templates/`](templates) — a project-conventions file, a PR template that
  makes the "capture this as a durable rule?" question a literal checklist
  item on every PR, and memory entry examples you can adapt.
- [`examples/illustrative-review-cycle/`](examples/illustrative-review-cycle)
  — a fully worked, generic example, told in prose: fake endpoint spec →
  plan → code review findings → verification report → a review round that
  sends the diff back → what gets captured as a durable rule afterward, and
  what doesn't.
- [`examples/harness-substrate/`](examples/harness-substrate) — a real,
  runnable Express + Sequelize (sqlite) app the harness actually operates
  on. The orchestration itself lives at the repo root: `.claude/agents/`
  defines the leader/implementer/reviewer roles, `.claude/settings.json`
  hooks enforce verification, `feature_list.json` and `progress/` hold
  real on-disk state, and `CHECKPOINTS.md` defines what "verified"
  objectively means. This is the difference between reading about the loop
  and running it.
- [`case-study/session-metrics.md`](case-study/session-metrics.md) —
  anonymized metrics from real usage.

## The harness is part of the repo, not a chat transcript

The executable pieces at the repo root (`CLAUDE.md`, `.claude/agents/`,
`.claude/settings.json`, `AGENTS.md`, `CHECKPOINTS.md`, `feature_list.json`,
`init.sh`) mirror
[betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes)
directly — file names, the leader/implementer/reviewer role split, the
C1-C5 "judge the destination, not the path" checkpoint format, and the
hooks-based enforcement all come from there, adapted from that repo's
Python/CLI substrate to `examples/harness-substrate/`'s Express + Sequelize
one. This is not an original interpretation of what a harness "should" look
like — it's the same mechanics applied to the API-engineering domain this
repo already documents.

Three things distinguish this from "paste `METHODOLOGY.md` into a chat and
hope the agent follows it":

1. **The repo is the system.** `CLAUDE.md` auto-loads the `leader` role for
   every session; `.claude/agents/`, `feature_list.json`, and `progress/`
   are versioned files, not conversation state — a new session picks up
   exactly where the last one left off by reading disk, not by being
   re-told.
2. **Orchestration is real, not simulated.** `leader` plans and delegates
   (and never edits code); `implementer` writes code against an approved
   plan only; `reviewer` runs real requests and independent review lenses.
   See `.claude/agents/`.
3. **The harness verifies itself, enforces that verification via hooks, and
   can be improved.** `.claude/settings.json`'s `Stop` hook runs `init.sh`
   before a session can end — the harness executes this, not the agent, so
   it can't be skipped by a confident-sounding report. `CHECKPOINTS.md`
   gives every stage an objective pass/fail bar. `progress/history.md` and
   `examples/harness-substrate/PROJECT-CONVENTIONS.md` are where a
   reviewer's stated rule (a tech lead's "Elliott rule," a corrected
   assumption) gets written down once so the *next* cycle already knows
   it — the LEARN stage in `METHODOLOGY.md` made literal.

## Relationship to existing tools

This methodology is designed to run on top of any AI coding agent that
supports custom slash-command-style skills (Claude Code, and similar tools).
It doesn't replace [Spec Kit](https://github.com/github/spec-kit) — it's a
narrower, API-specific application of the same underlying idea, plus a
verification and multi-agent review layer Spec Kit doesn't prescribe.

## License

MIT — see [`LICENSE`](LICENSE).
