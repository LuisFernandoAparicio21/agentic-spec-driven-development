# Case study: metrics from real usage

> Anonymized numbers from applying this methodology on a production
> Express + Sequelize REST API codebase. No source code, business domain
> details, or proprietary data appear below — only counts and outcomes.

## Delivery

- **52 pull requests merged** to the main development branch using this
  workflow, across a multi-month engagement.
- Endpoints built end-to-end in a single recent working session (spec →
  plan → implement → verify → multi-agent review → simplify → merge):
  multiple new REST endpoints across two related features, each following
  the same loop independently.

## What multi-agent review actually caught

- A **real concurrency bug**, found only through runtime verification, not
  static review: 15 concurrent identical requests against a "create" style
  endpoint resulted in 6 duplicated rows that should have been rejected as
  duplicates. The same non-atomic check-then-write pattern, tested against a
  sibling "update" (replace) style endpoint, produced a different failure
  mode under the same concurrent load — 12 of 15 requests "succeeded," but a
  lost-update pattern meant only the last one to finish was actually
  reflected, silently discarding the others. Same root cause, two different
  observable symptoms depending on the endpoint's write pattern — the kind
  of distinction that only shows up by actually running the concurrent
  load, not by reasoning about it.
- A **validation gap a fast human decision missed**: a quick, reasonable-
  sounding call to simplify a validation check (based on a real foreign-key
  constraint proving one condition) turned out to silently drop two
  *independent* status-flag checks on a different table that the constraint
  didn't cover. An 8-agent parallel review pass, followed by a dedicated
  single-purpose verifier agent, caught and confirmed the gap before it
  shipped; a fix was designed, applied, and re-verified in the same review
  cycle.
- Across review passes, **8 independently-angled agents** were run in
  parallel per pass (3 correctness lenses, 3 quality lenses, 1 altitude
  lens, 1 conventions lens), with findings that survived a dedicated
  verification pass — refuted findings (confirmed false, provably
  impossible, or already handled elsewhere) were dropped before reporting.

## Verification discipline

- Every new endpoint was run against a real request/response cycle before
  being called done — not just read.
- A standard negative-case battery (missing fields, wrong types, boundary
  values, SQL-injection-shaped strings, prototype-pollution-shaped payloads,
  oversized payloads, and concurrent-request batteries) was run against
  every new endpoint, not reserved for endpoints perceived as high-risk.
- Every test fixture written to exercise a real code path against a real
  database was cleaned up and the cleanup itself re-confirmed (row count
  checked back to baseline) before reporting success.

## What this is not

This case study is not a claim that every session ran perfectly the first
time — several review passes surfaced real issues that required a second
implementation pass before shipping. That's the methodology working as
designed: catching problems before a human is the only line of defense, not
a claim that problems never occur.
