# Token / Cost Usage Log

> Raw, growing dataset from real test runs of this methodology, logged as
> they happen so there's real data to optimize against later instead of
> guessing. Each row is one agent invocation. No source code or business
> details from any underlying project — just the shape of the task and the
> numbers.

## Why this exists

You can't optimize token/time cost from intuition alone — the actual
distribution of where cost goes (research vs. implementation vs.
verification vs. review) only shows up once there's enough real data. This
log is the raw material for that later analysis; it intentionally doesn't
try to draw conclusions yet; a handful of runs isn't a sample size, it's a
starting point.

## Columns

- **Task shape** — what kind of work, generically described (not the
  underlying project's specifics).
- **Scope** — isolated demo project vs. an existing, larger real codebase
  (this matters a lot for research cost — a fresh agent on a large codebase
  spends real tokens just finding the relevant precedent before it writes
  anything).
- **Outcome** — did it complete, and how it compared to a known-good
  reference implementation where one existed.
- **Tokens / Tool calls / Duration** — as reported by the agent invocation
  itself.
- **Notes** — anything that explains an outlier, good or bad.

## Log

| # | Task shape | Scope | Outcome | Tokens | Tool calls | Duration | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Blind end-to-end implementation of a new CRUD endpoint (plan → code → verify → self-review → simplify), following the full methodology from `METHODOLOGY.md` | Isolated demo project, one existing sibling resource as precedent | Completed. Verified independently afterward — matched a hand-written reference implementation closely, including correctly avoiding a validation bug (missing `.integer()` on a numeric field) that the reference example had specifically documented as an easy mistake. Its own review pass correctly refuted one of its own findings by citing the project's stated convention rather than accepting it uncritically. | 97,437 | 83 | ~14.7 min | Full loop including the agent spawning its own sub-agents for the multi-agent review phase — this is the most expensive run shape (nested orchestration), and it's the reference point for what "the whole loop, done thoroughly" costs. |
| 2 | Blind review/finish of an *already-implemented* endpoint on a real, existing, larger codebase, environment setup only (isolated worktree misconfigured — see notes) | Real, larger existing codebase | **Blocked before any implementation work** — the isolated environment it was given didn't contain the project at all (an empty worktree). Correctly stopped and asked for clarification instead of guessing or silently working around it, rather than assuming the pre-existing uncommitted diff it found in a different location was safe to overwrite. | 49,334 | 21 | ~55 sec | Not wasted spend — it's the cost of an agent correctly refusing to proceed on ambiguous/broken setup rather than the cost of doing real work. Logged as a distinct outcome category (**blocked**, not **failed** or **completed**) because conflating the two would understate how much of this run's cost was "safety," not "waste." Root cause was an isolation-tooling assumption on the orchestrating side, not the agent under test. |

## Open questions this log should eventually answer

- What fraction of total cost on a real (non-isolated-demo) codebase goes
  to research/precedent-finding vs. implementation vs. verification vs.
  review, once there's a large enough sample to break it down?
- Does the multi-agent review phase's cost scale roughly linearly with lens
  count, or are there fixed research costs shared across lenses that a
  smarter orchestration could pay once instead of N times?
- How much cheaper is a **review-only** pass (agent checks/finishes
  existing work) than a **blind-implementation** pass on a comparably-sized
  task, once a blocked-vs-completed run of each exists to compare?
