# Human-in-the-Loop Gates

## The principle

The goal is not to insert a human approval into every automated step — that
just turns a person into an expensive confirmation button. The goal is to
gate on **confidence, impact, and reversibility**: automate freely where a
mistake costs nothing to undo, and require an explicit human "go" exactly
where a mistake would be expensive, visible, or hard to reverse.

## The five patterns, and which ones this methodology uses

Human-in-the-loop design generally comes down to five recurring patterns.
This methodology leans on two of them deliberately and leaves the other
three as extensions a team can add if their risk profile calls for it:

1. **Approval Gate** *(used, mandatory)* — the agent prepares the action,
   states exactly what it's about to do and why, and pauses. A human
   approves, rejects, or redirects before anything executes. This is the
   only pattern used for commit/push/merge and any destructive or
   externally-visible action in this methodology — see the constitution in
   [`METHODOLOGY.md`](../METHODOLOGY.md#6-the-constitution-non-negotiable).
   The size of what's prepared for approval isn't fixed, though — the
   principle below (gate on impact/reversibility, not on every step)
   already implies that a pre-code gate for a genuinely unambiguous,
   single-file, precedent-backed change should be a three-line plan, not
   a three-document spec. `docs/07-spec-driven-development.md`'s Trivial
   shortcut is this same principle applied one level down, to the
   question of how much artifact a given gate needs before it's worth
   pausing for.
2. **Audit Trail with Lazy Review** *(used, for everything else)* — every
   plan, tool action, diff, and verification result is preserved so a human
   can reconstruct exactly how a result was produced, even for actions that
   didn't require synchronous approval. Nothing important disappears into an
   unreviewable black box.
3. **Confidence-Based Routing** *(optional extension)* — route low-risk,
   high-confidence actions to auto-proceed, and only pause for approval below
   a defined confidence or above a defined risk threshold. Not used by
   default here because API-layer changes (schema, validation, persisted
   data) are rarely low-enough-stakes to qualify — but a team with a large
   volume of genuinely low-risk changes (e.g. auto-generated boilerplate)
   may want to add this.
4. **Escalation Ladder** *(optional extension)* — route to progressively
   more senior/authoritative review as risk increases. Relevant for teams
   layering this methodology under an existing review-tier process.
5. **Collaborative Drafting** *(optional extension)* — human and agent
   iterate on the same artifact together in real time, rather than
   propose-then-approve. The planning phase already resembles this in
   practice (a plan gets redirected and re-proposed, not just accepted or
   rejected wholesale) but it isn't formalized as a distinct pattern here.

## What always requires an explicit gate

Regardless of how confident the agent is:

- committing, pushing, or merging code,
- any destructive or hard-to-reverse operation (force-push, hard reset,
  dropping data, deleting a branch),
- sending anything visible to people outside the immediate session (a PR
  comment, a message, a deployment),
- writing to a database outside of a reversible, self-cleaning test fixture.

Approval for one instance of any of the above is **not** standing approval
for the next one — scope the "yes" to exactly what was asked, not to the
category of action in general.

## Idempotency: the one practice that matters most

If a team adopts exactly one engineering discipline from this document, make
it this one: **every action an agent can take without a synchronous human
approval must be safe to run twice.** In practice, for API development, this
almost always means: every test fixture written to exercise a real code path
gets a symmetric, verified cleanup in the same pass (see
[`docs/03-runtime-verification.md`](03-runtime-verification.md)). An agent
that can safely retry, safely re-run a verification pass, or safely recover
from an interrupted session without accumulating side effects is an agent a
human can actually trust to work autonomously between approval gates —
which is the entire point of having gates instead of approving every single
step.

## The circuit breaker: bounded retries, not infinite loops

Idempotency makes it *safe* for an agent to retry a fix-and-reverify cycle
autonomously. It does not make it *wise* to retry indefinitely. If VERIFY
fails after a fix, fixing again and re-verifying is reasonable. If it fails
again after that fix, and again after the next one, continuing to loop
autonomously stops being productive iteration and starts being a sign the
agent is missing something a human would catch immediately — a wrong
assumption in the plan, a misunderstood spec, an environment problem no
amount of code changes will fix.

**Cap it.** After a small, fixed number of consecutive failed
verification attempts on the same issue (three is a reasonable default),
stop. Report exactly what was tried, what each attempt's verification
output showed, and why the next attempt isn't obviously going to be
different — and hand the decision to a human instead of trying a fourth
variation. This is the same principle production agent systems use to stop
cascading failures: open the circuit, don't keep hammering a path that
keeps failing the same way.

## Why not gate everything

An approval request for every file read, every research step, every
candidate finding turns the human into a rate limiter on the agent's actual
work, without adding safety — none of those actions are hard to reverse or
externally visible. Reserve the gate for where it earns its cost.
