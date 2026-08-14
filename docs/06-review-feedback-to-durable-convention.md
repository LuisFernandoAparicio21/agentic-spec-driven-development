# Closing the Loop: Review Feedback → Durable Convention

## The scenario this covers

This is, in practice, one of the most common cycles in real API development
with a human reviewer in the loop — common enough that it needs its own
named stage, not just a mention inside the memory docs:

> You open a PR. A reviewer sends it back — either for a **readability /
> convention** reason ("we don't brace single-statement if bodies here") or
> a **functionality** reason (a real bug, a missed edge case). You fix it.
> The PR merges.

If the loop stops there, the next endpoint someone (human or agent) builds
on this project hits the *exact same reviewer comment again* — because
nothing outside that one conversation remembered it. This is the failure
mode this stage exists to close.

## Why this needs to be its own stage, not just "part of memory"

It's easy to write "capture learnings" as a bullet inside a general memory
doc and never actually do it, because nothing in the main loop forces the
question. This methodology puts **LEARN** as an explicit stage after the
human gate for exactly that reason:

```
   ... -> VERIFY -> SIMPLIFY -> HUMAN GATE (commit/push/merge) -> LEARN -> (loop closes back into Context Delivery)
```

Every time a human approves, rejects, or comments on a diff, that's a
signal-generating event. The LEARN stage asks one question before the
session is considered closed: **did anything happen in this cycle that
should outlive this session?**

## The decision: one-off fix, or durable rule?

Not every review comment needs to become a persisted rule — see
[`docs/04-memory-institutional-knowledge.md`](04-memory-institutional-knowledge.md)
for the general filter. For review-feedback specifically, ask:

1. **Is this specific to this one diff, or a pattern that will recur on the
   next similarly-shaped endpoint?** A typo fix is one-off. "This project
   never braces single-statement if bodies" will recur on every future
   validator.
2. **Was this a correction, or a confirmation?** Both matter, and both are
   captured the same way — a confirmation ("yes, that unusual choice was
   correct, keep doing it") prevents the *next* agent from "fixing" a
   deliberate decision back to the more obvious-looking approach.
3. **Capture on the first occurrence — don't wait for a second one.** Waiting
   for a comment to repeat before writing it down means it *will* repeat at
   least once, on a real diff, costing a real review cycle. The cost of
   writing down a rule that turns out to be one-off is low (skip it or
   retire it later); the cost of not writing down a rule that recurs is a
   repeated review comment on a future PR, which is a real, avoidable delay.

## Making it a real step, not a good intention

The failure mode isn't "nobody knows this stage should happen" — it's that
without something forcing the question, it quietly gets skipped under
deadline pressure, every time, indefinitely. Don't rely on an agent (or a
human) remembering to do this unprompted. Put it in the PR itself:
[`templates/PULL_REQUEST_TEMPLATE.md`](../templates/PULL_REQUEST_TEMPLATE.md)
has a "before merging" checklist that asks this question explicitly, on
every PR, and asks the *reviewer* — not just the author — to hold the
answer to account before approving. That's what turns this from a
methodology principle into something that actually survives contact with a
real sprint deadline.

## Where it goes

- **A rule about how code in this project should be written** (the
  readability/convention case) → append to the project-conventions file
  (see [`templates/PROJECT-CONVENTIONS.md.template`](../templates/PROJECT-CONVENTIONS.md.template)'s
  "Recurring reviewer conventions" section), dated, in the reviewer's own
  terms where possible.
- **A rule about a specific mistake and how to detect it** (the
  functionality case) → a `lesson`-type memory (see
  [`templates/memory-entry-examples/lesson-example.md`](../templates/memory-entry-examples/lesson-example.md)).
- **A rule that's really about how to *approach* a class of work**, not a
  code-style detail → a `feedback`-type memory (see
  [`templates/memory-entry-examples/feedback-example.md`](../templates/memory-entry-examples/feedback-example.md)).

The project-conventions file and the memory store aren't competing places
for the same thing — the conventions file is what every session loads in
full, every time (see
[`docs/04-memory-institutional-knowledge.md`](04-memory-institutional-knowledge.md#the-read-discipline)),
so it's the right home for a rule that should apply to *every* future diff
in this project, unconditionally. Memory is for everything narrower than
that — a specific bug class, a decision that applies in a specific
situation, a fact about current project state.

## The dated-marker convention

Every rule appended to the project-conventions file as a result of this
stage gets a trailing marker noting when it was captured:

```
- No `{}` on `if`/`else` bodies that are a single statement. <!-- learned: 2026-08-14 -->
```

This turns the conventions file into its own lightweight audit trail: a
future reader (human or agent) can see not just *what* the rules are, but
*when* each one was established — useful for distinguishing "this has been
the rule since day one" from "this was just decided," and for catching a
rule that's gone stale (referencing a function or pattern that's since been
removed from the codebase).

## Worked example

See [`examples/illustrative-review-cycle/05-review-rejection.md`](../examples/illustrative-review-cycle/05-review-rejection.md)
and [`06-captured-convention.md`](../examples/illustrative-review-cycle/06-captured-convention.md)
for a full, concrete walkthrough of this stage applied to the same
invented `widgets` endpoint used throughout the other examples: a reviewer
sends back a functionality issue and a readability issue on the same diff,
both get fixed, and only the readability one turns out to be a recurring
pattern worth a durable rule — the functionality one was genuinely specific
to that one field and is captured as a narrower lesson instead.
