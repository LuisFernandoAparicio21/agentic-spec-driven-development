# Memory & Institutional Knowledge

## The problem

An agent session ends and everything it learned ends with it — a reviewer's
unwritten convention, a bug class specific to this stack, a gotcha about how
a shared utility actually behaves. The next session re-derives the same
lesson, sometimes by repeating the same mistake, unless something outside
the conversation carries it forward.

## The taxonomy

Borrowing the framing used by modern agent-memory systems (episodic /
semantic / procedural memory), institutional knowledge for API development
splits cleanly into four practical categories:

| Category | What it captures | Roughly maps to |
|---|---|---|
| **Lesson** | A mistake happened once; here's what, why, and how to detect it next time | Episodic memory |
| **Feedback** | A human corrected or confirmed an approach — the *rule*, why, and when it applies | Procedural memory |
| **Project** | A fact about the current state of the work — what's blocked, what's pending, who decided what | Episodic memory (time-bound) |
| **Reference** | A pointer to where durable information lives — an external doc, a technique, a location | Semantic memory |

## What makes a memory worth writing down

Not everything is worth persisting. A good filter:

- **Would repeating this mistake cost more than writing it down once?** If
  yes, it's a lesson.
- **Did a human correct the same thing twice, or explicitly confirm an
  unusual choice without pushback?** If yes, it's feedback — corrections are
  easy to notice; confirmations are quieter and easy to miss, but just as
  valuable (they stop the agent from "fixing" something that was already a
  deliberate decision).
- **Is this a fact that will go stale in days or weeks** (a sprint state, a
  pending PR)? It's project memory — write it with an explicit date so a
  future read knows whether it's still current.
- **Is this a reusable technique or an external pointer**, not project
  state? It's a reference.

## What NOT to persist

- Anything derivable by reading the current code — conventions, file
  structure, architecture. Point at the project-conventions file instead of
  duplicating it into memory.
- Git history — `git log`/`git blame` are already authoritative and current;
  a memory snapshot of "who changed what" goes stale immediately.
- Ephemeral in-conversation state (a task list for the current session) —
  that belongs in a task tracker, not long-term memory.

## The write discipline

1. **Surface liberally, write conservatively.** When reviewing a session for
   learnings, propose every plausible candidate — a missed learning costs a
   repeated mistake; a false one, written to disk without confirmation,
   corrupts every future session that trusts it. Confirm candidates with a
   human before writing anything.
2. **Never silently overwrite.** Append, or create a new file — a memory
   that turns out to be wrong should be marked outdated, not have its
   history erased.
3. **Every memory is a point-in-time claim.** A memory that names a specific
   function, file, or behavior may have been renamed or removed since it was
   written. Before acting on a recalled memory — not just mentioning it —
   verify it still holds against the current code.
4. **Link related memories to each other.** A lesson about a specific bug
   class and a project note about where that bug class recurred should
   reference each other, so a future read gets the full context, not a
   fragment.

## The read discipline

At the start of a session (or before a non-trivial change), load:

- the project-conventions file in full,
- an index of available memories (titles + one-line hooks, not full content
  — keep this scannable),
- only the full content of memories relevant to the current task, pulled in
  on demand.

This mirrors how modern agent-memory systems retrieve at session start:
semantic/keyword relevance first, full detail only when it's actually
needed — not the entire memory store loaded into every context regardless
of relevance.

## See also

[`templates/memory-entry-examples/`](../templates/memory-entry-examples) for
the concrete file format used for each category.
