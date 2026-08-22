# Multi-Agent Review

## Purpose

Catch what a single reviewer — human or AI — misses, by running several
independently-angled reviews in parallel and only trusting a finding once
it's been checked a second time.

This is the "Multi-Agent Swarms" pattern (see
[awesome-agent-orchestrators](https://github.com/andyrewlee/awesome-agent-orchestrators)):
several specialized agents working toward the same goal, coordinated by a
single orchestrating pass, rather than one generalist agent trying to hold
every lens in its head at once.

## The two-phase structure

### Phase 1 — Fan-out: independent finder agents

Launch several agents **in parallel, in a single batch** — not sequentially.
Each one gets the *same diff* but a *different lens*:

**Correctness lenses** (bugs — wrong output, crashes, dropped behavior):
- **Line-by-line scan.** Read every changed line and the function it lives
  in; ask what input or timing makes this line wrong.
- **Removed-behavior audit.** For everything the diff deletes, name the
  invariant it enforced and check the invariant is re-established somewhere
  else — or flag that it isn't.
- **Cross-file tracer.** For every changed function, find its callers and
  callees; check the change doesn't break an assumption either side is
  making.

**Quality lenses** (not bugs — cost, not crashes):
- **Reuse.** Does the diff reimplement something the codebase already has?
- **Simplification.** Is there redundant state, copy-paste, or dead code the
  diff leaves behind?
- **Efficiency.** Does the diff do wasted work — redundant DB round-trips,
  sequential work that could be independent, blocking work on a hot path?
- **Altitude.** Is the fix implemented at the right depth, or is it a
  narrow bandaid on a problem that's really structural?

**Convention lens:**
- **Project conventions.** Check the diff against the project's own written
  conventions file (see [`templates/PROJECT-CONVENTIONS.md.template`](../templates/PROJECT-CONVENTIONS.md.template)).
  Only flag something here if you can quote the exact rule and the exact
  line breaking it — this lens is not a place for style opinions.

Each finder agent returns candidates independently, with **no visibility
into what the others found.** This independence is the entire point — an
agent that already knows "the correctness pass found nothing" is biased
toward finding nothing itself.

### Phase 2 — Fan-in: verification and confidence scoring

Once every finder has returned:

1. **Deduplicate.** If two agents flag the same defect at the same location
   for the same reason, that's one finding, not two — but note that it was
   independently confirmed (see scoring below).
2. **Verify each remaining candidate independently.** A separate verifier
   agent — not the one that found it — checks the candidate against the
   actual code and returns exactly one of: **confirmed**, **plausible**, or
   **refuted**. Bias this step toward keeping findings: a concurrency race,
   a rare-but-reachable null path, or an edge case the code doesn't exclude
   should be kept as *plausible*, not thrown out for being "unlikely."
   Refute only when the finding is factually wrong, provably impossible, or
   already handled elsewhere in the diff.
3. **Score confidence by agreement, not by a single pass's certainty.** A
   finding independently surfaced by two or more different lenses (e.g. both
   the correctness scan *and* the altitude review flag the same missing
   check, from different angles) is higher-confidence than a finding only
   one lens noticed. Report that agreement explicitly — it's information the
   human reviewer would otherwise have to reconstruct by reading every
   sub-report themselves.
4. **Rank and cap.** Correctness findings always outrank quality findings
   when something has to be cut for length. Report the most severe first.

## What ships to the human

Every surviving finding, ranked, each with: the file and line, a one-sentence
statement of the defect, and a concrete failure scenario (specific input or
state that triggers it — not "this could be a problem"). A finding without a
constructible failure scenario doesn't ship.

## Why not just one thorough agent?

A single agent reviewing its own (or another agent's) diff tends to
anchor on the change's stated intent and check "does this do what it says,"
which is exactly the failure mode that lets a plausible-looking bug through.
Splitting the same diff across genuinely independent lenses — each blind to
the others' output until the verification step — reproduces the value of
independent human reviewers without the calendar cost of asking three people
to each carve out review time.

## Fan-out isn't free — bound it deliberately

Every parallel agent is real time and real cost, not a free resource. Scale
the number of lenses to the size and risk of the diff, not by default to
the maximum every time — a five-line fix to an existing endpoint doesn't
need all eight lenses from this doc; a new endpoint touching several files
does. Treat the lens count as a dial, not a fixed constant, and prefer
fewer lenses run well over the maximum number run superficially.

Concrete threshold (see `.claude/agents/leader.md`'s escalation table,
which this mirrors so the rule lives as an enforceable table, not just
this paragraph): diffs under ~15 lines in one file skip the separate
review pass entirely — VERIFY plus the implementer's own CHECKPOINTS.md
pass is enough. ~15-60 lines get 1-2 lenses. Over that or spanning more
than 2 files gets 3-4. Reserve the full 8-lens spread for genuinely
high-risk changes (auth, money, data migrations touching a shared
production database) — not the default case.
