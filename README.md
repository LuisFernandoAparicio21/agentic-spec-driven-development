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
- [`docs/`](docs) — one deep-dive per phase, including
  [`06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md)
  — the "PR gets sent back → fix it → decide if it's a durable rule" cycle,
  one of the most common and easiest-to-skip stages in practice.
- [`templates/`](templates) — a project-conventions file, a PR template that
  makes the "capture this as a durable rule?" question a literal checklist
  item on every PR, and memory entry examples you can adapt.
- [`examples/illustrative-review-cycle/`](examples/illustrative-review-cycle)
  — a fully worked, generic example: fake endpoint spec → plan → code review
  findings → verification report → a review round that sends the diff back
  → what gets captured as a durable rule afterward, and what doesn't.
- [`case-study/session-metrics.md`](case-study/session-metrics.md) —
  anonymized metrics from real usage.

## Relationship to existing tools

This methodology is designed to run on top of any AI coding agent that
supports custom slash-command-style skills (Claude Code, and similar tools).
It doesn't replace [Spec Kit](https://github.com/github/spec-kit) — it's a
narrower, API-specific application of the same underlying idea, plus a
verification and multi-agent review layer Spec Kit doesn't prescribe.

## License

MIT — see [`LICENSE`](LICENSE).
