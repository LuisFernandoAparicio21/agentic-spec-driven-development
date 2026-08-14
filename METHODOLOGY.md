# Methodology: Agentic Spec-Driven Development for APIs

## 1. The problem this solves

There are two common failure modes when an AI agent writes API code:

- **Vibe-coding.** The agent is told "add an endpoint for X" and starts
  writing route handlers immediately. It guesses at validation rules, invents
  its own error-message shape, and never runs the endpoint against a real
  database. The diff looks plausible. It ships broken.
- **Unverified confidence.** The agent writes correct-looking code, the
  developer skims it, it merges. Nobody actually sent a request to the
  running server. The first real signal is a bug report.

Both failure modes share a root cause: **the agent's output was never
observed running, and no second opinion was ever consulted before a human
had to be the only line of defense.** This methodology closes both gaps by
making two things mandatory, not optional: a reviewable plan before code, and
a runtime observation before "done."

## 2. The workflow in practice

```
   ┌─────────┐  ┌───────────┐  ┌────────┐  ┌────────┐  ┌──────────────────┐  ┌──────────┐  ┌─────────────┐  ┌───────┐
   │  SPEC   │->│   PLAN    │->│  CODE  │->│ VERIFY │->│  MULTI-AGENT      │->│ SIMPLIFY │->│ HUMAN GATE  │->│ LEARN │
   │ method, │  │ files to  │  │ route/ │  │ real   │  │  REVIEW           │  │ cleanup  │  │ commit/push/│  │ capture│
   │ URL,    │  │ touch,    │  │ valid- │  │ HTTP + │  │  (parallel agents,│  │ pass     │  │ merge —     │  │ rules  │
   │ params, │  │ reused    │  │ ator/  │  │ real DB│  │  independent      │  │          │  │ explicit    │  │ or say │
   │ response│  │ helpers   │  │ ctrl   │  │        │  │  verification)    │  │          │  │ human "go"  │  │ nothing│
   └─────────┘  └───────────┘  └────────┘  └────────┘  └──────────────────┘  └──────────┘  └─────────────┘  └───┬───┘
        ^                                                                                                        │
        └───────────────────────── durable rules feed back into Context Delivery for the next SPEC ──────────────┘
```

Each stage produces an artifact. Nothing advances to the next stage without
the previous artifact existing and being approved (for the human-facing
stages) or passing (for the automated ones). LEARN is not optional
busywork tacked on at the end — it's the stage that decides whether
anything from this cycle needs to outlive this session, and it's what
makes the loop actually a loop instead of a straight line that forgets
everything between runs. See
[`docs/06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md).

### SPEC

A one-paragraph, unambiguous statement of the contract: HTTP method, URL,
required/optional params and their types, and the exact shape of a successful
response. If the spec is ambiguous (e.g., "update the user" — which fields?
partial or full replace?), the agent stops and asks before touching code.
Ambiguity resolved here is cheap; ambiguity resolved after code exists is not.

### PLAN

Before any file is written, the agent researches the existing codebase for
the closest precedent (a sibling endpoint that already solves a similar
shape of problem) and produces a plan naming:

- the exact files that will be created or changed (route, validator,
  controller — rarely more),
- which existing helpers/utilities will be reused instead of rewritten,
- the validation rules and their exact error messages,
- how the change will be verified.

This plan is a reviewable artifact. A human approves it — or redirects it —
**before implementation starts.** This is the single highest-leverage gate in
the whole loop: catching a wrong assumption in a plan costs a sentence;
catching it after code, tests, and a review pass exist costs all of that
work.

### CODE

Implementation follows the approved plan exactly. Deviating from the plan
without flagging it back to the human defeats the purpose of having approved
one.

### VERIFY

The endpoint is actually run. A real HTTP request goes to a real running
instance of the service, against a real (or realistic staging) database.
The response is captured and compared to the spec. See
[`docs/03-runtime-verification.md`](docs/03-runtime-verification.md) — this
is the phase most agentic workflows skip, and the one that catches the bugs
static review can't. Run it again after any fix produced by the next two
stages — a fix that isn't re-verified is just a new, unverified claim.

### MULTI-AGENT REVIEW

The diff is reviewed by several independent agents in parallel, each
assigned a different lens (see [`docs/02-multi-agent-review.md`](docs/02-multi-agent-review.md)
for the full mechanics). This is not one agent reading its own code back —
it is genuinely independent review, run the same way you'd want independent
human reviewers: nobody sees anyone else's notes until everyone is done.

### SIMPLIFY

A pass focused purely on quality, not correctness: is there duplicated logic
that should reuse an existing helper, is there a cheaper way to do the same
work, is the change implemented at the right layer. Correctness is already
settled by the review + verify stages — this stage is about not leaving a
mess behind.

### HUMAN GATE

Nothing is committed, pushed, or merged without explicit human confirmation.
See [`docs/05-human-in-the-loop-gates.md`](docs/05-human-in-the-loop-gates.md).
This is also where a human reviewer — not just the automated review stage —
gets the chance to send the diff back, which is exactly the trigger for the
next stage.

### LEARN

This is the stage most agentic workflows skip entirely, and skipping it is
why the same review comment shows up again on the next PR. Before the cycle
is considered closed, ask: did anything happen here — a correction, a
confirmed judgment call, a bug class specific to this stack — that should
outlive this session? If yes, capture it now, not "later." See
[`docs/06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md)
for the full decision process, and
[`docs/04-memory-institutional-knowledge.md`](docs/04-memory-institutional-knowledge.md)
for where captured knowledge lives and how it's retrieved next time. This is
the stage that turns the diagram above from a straight line into an actual
loop — a durable rule captured here changes what the *next* SPEC's Context
Delivery looks like, before that next cycle even starts.

## 3. Why this matters now

Three trends make this worth formalizing instead of improvising per session:

1. **Agents can generate a correct-looking diff faster than a human can read
   it carefully.** Review capacity, not generation capacity, is now the
   bottleneck — which is exactly what multi-agent review is designed to
   relieve without removing the human from the final decision.
2. **API surfaces compound.** A backend with dozens of endpoints has dozens
   of chances for the same class of mistake (missed validation, inconsistent
   error shapes, an unverified edge case) to repeat. A documented, reusable
   loop prevents each new endpoint from re-deriving lessons the last one
   already paid for.
3. **"It compiles" and "the tests pass" are not the same claim as "I sent it
   a request and watched it work."** As agents write more of the test suite
   too, a runtime-observation step that isn't just "run the tests I also
   wrote" becomes the load-bearing check.

## 4. Core principles

1. **A plan is cheaper to fix than code.** Get explicit approval on the plan
   before writing the implementation.
2. **Verification is runtime observation, not code reading.** Running the
   endpoint and capturing its actual output is evidence. Everything else is
   a claim about the code.
3. **Confidence comes from independent agreement, not a single opinion.** A
   finding that two independently-angled review passes both surface is worth
   more than one agent's single pass, however thorough. See
   [`docs/02-multi-agent-review.md`](docs/02-multi-agent-review.md) for how
   this is scored in practice.
4. **Every test fixture is reversible by default.** If a verification step
   needs to write data to check a real code path, that write must have a
   symmetric cleanup step in the same pass. Treat this as non-negotiable, not
   as a nice-to-have — it's the one practice that keeps an agent trustworthy
   around a real database.
5. **Mutating actions require an explicit human "go."** Commit, push, merge,
   destructive database writes, anything visible to other people — the agent
   proposes, a human decides. See
   [`docs/05-human-in-the-loop-gates.md`](docs/05-human-in-the-loop-gates.md).
6. **Institutional knowledge survives the session.** A lesson learned once
   (a reviewer's convention, a bug class, a gotcha in the stack) is written
   down so the next session starts already knowing it, instead of re-deriving
   it. See [`docs/04-memory-institutional-knowledge.md`](docs/04-memory-institutional-knowledge.md).
7. **A rejected diff isn't done when the fix is done — it's done when the
   question "should this become a durable rule?" has been asked and
   answered.** Capture on the first occurrence a pattern is likely to
   recur, not the second. See
   [`docs/06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md).

## 5. The harness

Borrowing the taxonomy from
[awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)
— the scaffolding around the agent determines its success more than the
model does. Here's how each primitive maps to a concrete piece of this
methodology:

| Harness primitive | Concrete implementation here |
|---|---|
| Planning & Task Decomposition | The PLAN stage — file-by-file, precedent-grounded |
| Context Delivery | A project-conventions file (see [`templates/PROJECT-CONVENTIONS.md.template`](templates/PROJECT-CONVENTIONS.md.template)) loaded every session |
| Memory & State | Structured, categorized memory files, retrieved at session start and written during the LEARN stage — see [`docs/04-memory-institutional-knowledge.md`](docs/04-memory-institutional-knowledge.md) and [`docs/06-review-feedback-to-durable-convention.md`](docs/06-review-feedback-to-durable-convention.md) |
| Task Runners & Orchestration | Parallel fan-out to independently-angled review agents |
| Verification & CI Integration | The VERIFY stage — real requests, real responses, captured as evidence |
| Human-in-the-Loop | Explicit approval gates before any mutating or externally-visible action |
| Permissions & Authorization | A fixed, written set of actions that always require a human "go" regardless of confidence |

## 6. The constitution (non-negotiable)

These are not defaults to override under time pressure — they're the reason
the rest of the methodology is trustworthy enough to move fast with:

1. Never commit, push, merge, or take a destructive/irreversible action
   without an explicit, current-turn human confirmation. Approval for one
   action is not standing approval for the next one.
2. Never claim "verified" without having actually run the code and captured
   its output. A clean static review is not verification.
3. Every database write made purely for testing purposes is cleaned up in
   the same pass, before reporting success.
4. When a plan and the implementation diverge, stop and say so — don't
   silently reconcile them.
5. A review finding that can't be traced to a concrete file, line, and
   failure scenario doesn't ship as a finding — vague findings erode trust
   in the ones that are real.
