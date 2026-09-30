<div align="center">

# Agentic Spec-Driven Development for API Engineering

**A production-tested methodology for building REST APIs with an AI agent as a real collaborator — not autocomplete, not "vibe-coding".**

<br>

![Methodology](https://img.shields.io/badge/method-spec--driven-2563EB?style=for-the-badge)
![Node](https://img.shields.io/badge/Node.js-Express%204-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Sequelize](https://img.shields.io/badge/ORM-Sequelize-52B0E7?style=for-the-badge&logo=sequelize&logoColor=white)
![Claude Code](https://img.shields.io/badge/agent-Claude%20Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-16A34A?style=for-the-badge)

<sub>Every endpoint goes through the same loop, every time, no shortcuts.</sub>

</div>

---

## Table of Contents

- [The Loop](#the-loop)
- [The Harness](#the-harness)
- [Why It Exists](#why-it-exists)
- [Validated Stack](#validated-stack)
- [Start Here](#start-here)
- [The Harness Is Part of the Repo](#the-harness-is-part-of-the-repo)
- [SDK Batch Verifier](#sdk-batch-verifier)
- [Relationship to Other Tools](#relationship-to-other-tools)
- [License](#license)

---

## The Loop

This is not a generic software methodology. It is **specialized** for the real shape of backend work: a request arrives as a *route*, a *validator* decides whether it's well-formed, a *controller* talks to the database, and a *response* goes out. That specificity is what makes it fast to apply and easy to verify.

```
  SPEC ──▶ PLAN ──▶ CODE ──▶ VERIFY ──▶ REVIEW ──▶ SIMPLIFY ──▶ HUMAN GATE ──▶ LEARN
   │                                                                             │
   └───────────────── the learned rule feeds the next SPEC ◀─────────────────────┘
```

---

## The Harness

The agent does not "remember" in the chat: state lives on disk. A new session resumes by reading files, not by being re-told.

```
  pending ─▶ spec_ready ─▶ ⏸ HUMAN GATE ─▶ in_progress ─▶ done
              (spec_author)                (implementer → reviewer)
                                                  │
                                       ✗ rejected ─┘  back to in_progress
```

| Role | Responsibility |
|------|----------------|
| **leader** | Decomposes and coordinates. Never writes code. Never marks `done`. |
| **spec_author** | Writes `requirements` / `design` / `tasks` in EARS notation. Does not implement. |
| **implementer** | One feature against an approved plan. Self-verifies with `init.sh`. |
| **reviewer** | Real VERIFY (HTTP + database) + multi-lens review. Approves or rejects. |

---

## Why It Exists

- [GitHub Spec Kit](https://github.com/github/spec-kit) (128k ★) proved that writing the plan as a reviewable artifact **before** any code exists works at general-purpose scale.
- This repo takes that idea and **narrows it to one domain**: API endpoint development — where the *spec* is a request/response contract, the *verification* is a real HTTP call against a real database, and the *review* is a set of specialized agents inspecting the diff from different angles before a human ever has to.
- It was born and used **in production**, across dozens of merged pull requests on a real Express + Sequelize backend.
- **No source code, business logic, or proprietary data** from that project appears here. Everything is generic and illustrative.

---

## Validated Stack

The **methodology** (the loop, the principles, the review / verify / learn stages) is stack-agnostic by design. The **templates and examples** reflect the one stack it was actually proven against — and are honest about it.

| Layer | Technology |
|-------|------------|
| Runtime / framework | Node.js + Express 4 |
| Validation | Joi |
| ORM / database | Sequelize (SQL Server via `tedious`; applies to any supported DB) |
| Architecture | Three-layer `routes → validators → controllers` |

> **Adapting it to another stack** (FastAPI + Pydantic, Go, a different ORM) means rewriting `PROJECT-CONVENTIONS.md.template` and the example code. The stages, review lenses, and verification discipline in `METHODOLOGY.md` and `docs/` carry over unchanged: none of them are written in terms of Express, Joi, or Sequelize.

---

## Start Here

| Resource | What you'll find |
|----------|------------------|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The full methodology: why it works, the workflow in practice, principles, and non-negotiable guardrails. |
| [`AGENTS.md`](AGENTS.md) | The entry point for an agent operating *inside* the repo: who does what, where state and rules live. |
| [`docs/`](docs) | One deep-dive per phase, including [the durable-convention cycle](docs/06-review-feedback-to-durable-convention.md): "the PR comes back → fix it → decide if it's a rule". |
| [`templates/`](templates) | Project conventions, a PR template that turns "capture this as a rule?" into a literal checklist item, and memory-entry examples. |
| [`examples/illustrative-review-cycle/`](examples/illustrative-review-cycle) | A full worked example in prose: fake spec → plan → findings → verification → a round that rejects the diff → what gets captured as a rule. |
| [`examples/harness-substrate/`](examples/harness-substrate) | A **real, runnable** Express + Sequelize (sqlite) app the harness actually operates on. |
| [`case-study/session-metrics.md`](case-study/session-metrics.md) | Anonymized metrics from real usage. |

---

## The Harness Is Part of the Repo

Three things set it apart from "paste `METHODOLOGY.md` into a chat and hope the agent follows it":

1. **The repo is the system.** `CLAUDE.md` auto-loads the `leader` role every session; `.claude/agents/`, `feature_list.json`, and `progress/` are versioned files, not conversation state — a new session resumes by reading disk.
2. **Orchestration is real, not simulated.** `leader` plans and delegates (never edits code); `implementer` writes against an approved plan; `reviewer` runs real requests and independent review lenses.
3. **The harness verifies itself and enforces it via hooks.** The `Stop` hook in `.claude/settings.json` runs `init.sh` before a session can close — the harness runs it, not the agent, so it can't be skipped by a confident-sounding report. `CHECKPOINTS.md` gives every stage an objective pass / fail bar.

> The mechanics (file names, the role split, the C1-C5 checkpoint format, hook-based enforcement) are modeled on [betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes), adapted from its Python/CLI substrate to the Express + Sequelize one here.

---

## SDK Batch Verifier

The interactive flow runs through Claude Code. `scripts/anthropic_sdk_examples/` adds a second mode for the same harness: the **Anthropic Python SDK called directly**, for batch checks and CI where no interactive session exists.

```
  spec_author.md ┐
  docs/07 (SDD)  ├─▶ SYSTEM (rules, ~5k tokens, cached) ─┐
  CHECKPOINTS.md ┘                                       ├─▶ Claude API ─▶ JSON verdict
  specs/<id>/*.md ──▶ USER (the spec under review) ──────┘                 APPROVED | CHANGES_REQUESTED
                                                                           + issues[]
  verify_batch.py
    spec #1 alone (writes the cache) ─▶ specs #2..N in parallel (read the cache)
                                                 │
                                   report.md + exit 1 if any spec is not APPROVED
```

- **Prompt caching:** the rules go in the system prompt with `cache_control: ephemeral`; only the spec changes per call. The first call writes the cache, later calls read it at about 5% of the input price. A live test asserts `cache_read_input_tokens > 0` on the second call.
- **Structured output:** the verdict is schema-validated JSON, so `jq` and CI can consume it.
- **Forced verification, no human in the loop:** same rules, applied the same way to every spec.

See [`scripts/anthropic_sdk_examples/README.md`](scripts/anthropic_sdk_examples/README.md) for install, usage and the tests.

---

## Relationship to Other Tools

It runs on top of any AI agent that supports slash-command-style skills (Claude Code and similar). It doesn't replace [Spec Kit](https://github.com/github/spec-kit): it's a narrower, API-specific application of the same underlying idea, plus a verification and multi-agent review layer that Spec Kit doesn't prescribe.

---

## License

**MIT** — see [`LICENSE`](LICENSE).

<div align="center"><sub>Built with the discipline it documents.</sub></div>
