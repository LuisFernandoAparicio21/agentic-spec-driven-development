# Runtime Verification

## The core rule

**Verification is runtime observation. Nothing else is.** You build the
endpoint, run the service, send it a real request, and capture what actually
comes back. That capture is your evidence. A clean code read, a passing
static review, a confident-sounding summary — none of those are evidence.
They're claims about the code.

## Why this is a separate, mandatory phase

It's tempting to treat multi-agent review as sufficient — several
independent passes already read the diff carefully, what's left to check?
The answer: everything that only shows up when the code actually executes
against real state. A validator that looks correct can still throw on a null
it never expected in practice. A query that reads correctly can still return
the wrong rows against real data shapes. Static review catches a different
class of problem than runtime observation does; neither substitutes for the
other.

## What counts as verification

- Start the actual service (or the smallest faithful stand-in for it — see
  "cold-start environments" below).
- Send a real HTTP request to the real endpoint.
- Capture the actual response body and status code.
- For endpoints that write data, read the write back from the database and
  confirm it matches what was sent — don't just trust a `{"status":true}`
  response.

## What does not count

- Importing the handler function directly and calling it in a script. If the
  real caller is HTTP, go through HTTP — a direct function call skips the
  routing layer, the body parser, and anything else that sits between a
  client and your code.
- Reading the test suite and confirming the assertions match the
  implementation. That's code review with extra steps, not observation.
- "The code looks right and follows the same pattern as an endpoint that
  already works." Patterns can be followed incorrectly in ways only runtime
  reveals (a typo'd function name that exists but does something slightly
  different, an off-by-one in a range check, a validation order that changes
  behavior).

## The negative-case battery

A verification pass that only exercises the happy path is half a
verification pass. For every new endpoint, also send:

- a request missing each required field, one at a time,
- a request with each field given the wrong type (string where a number is
  expected, an object where a string is expected),
- a request that should trigger every distinct rejection message the
  validator can produce (not just the first one you find),
- for endpoints under any kind of uniqueness or existence constraint, several
  concurrent identical requests — confirm the constraint actually holds
  under concurrency, not just sequentially.

Each of these is a real request against the real running service. A negative
case you only reasoned about instead of sending is not verified.

## The brute-force / security battery

The negative-case battery above checks that the endpoint rejects *malformed*
input correctly. This battery checks that it survives *adversarial* input —
a distinct, mandatory pass, not an optional extra for endpoints that "seem"
security-sensitive. Every new endpoint gets this battery regardless of how
low-risk it looks; a plain-looking create endpoint is exactly where a
missed check is most likely to slip through unnoticed. The categories below
map to real, named vulnerability classes — see
[OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
and [shieldfy/API-Security-Checklist](https://github.com/shieldfy/API-Security-Checklist)
for the full, general-purpose versions this battery is scoped down from:

- **Injection.** A SQL-injection-shaped string (`'; DROP TABLE ...;--`) in
  every free-text field — confirm it's stored as inert literal text, not
  executed, and the table still exists afterward. For a JS/Node stack
  specifically, also send a payload containing a `__proto__` or
  `constructor.prototype` key (**prototype pollution**) — confirm it's
  ignored or rejected, not silently merged into the object.
- **Mass assignment.** Add fields to the request body that aren't in the
  spec at all — especially anything that sounds privileged (`role`,
  `isAdmin`, `id`, a status flag the endpoint shouldn't let a client set
  directly). Confirm the API rejects the unknown field or silently drops
  it — never that it gets applied.
- **Broken object-level authorization (BOLA).** For any endpoint that takes
  an id referencing a specific record, send an id that exists but belongs
  to a different user/tenant/owner than the one making the request.
  Confirm the response is a clean rejection, not the other party's data —
  this is the single most common real-world API vulnerability class, and a
  plain existence check (`does this id exist?`) does not cover it; an
  existence check and an authorization check are two different questions.
- **Oversized payload.** A body well beyond whatever your framework's
  default size limit is. Confirm a clean rejection (not a crash, not a
  hang) — this is usually the framework's own behavior, but confirm it for
  this specific endpoint rather than assuming.
- **Rate limiting / brute force.** For any endpoint that gates access to
  something (login, a lookup by a guessable identifier, anything an
  attacker would want to hammer), send a rapid burst of requests and
  confirm there's a throttling or lockout behavior — or, if there
  deliberately isn't one yet, record that as a known gap in the
  project-conventions file (see
  [`docs/06-review-feedback-to-durable-convention.md`](06-review-feedback-to-durable-convention.md)),
  not as a silently accepted absence.

As with the negative-case battery, each of these is a real request sent to
the real running service, with the real response captured — not a
description of what "should" happen.

## Cold-start environments

Sometimes the "real" service can't run as-is in your environment — missing
credentials for a dependent system, a frontend you don't have locally,
infrastructure that only exists in a deployed environment. In that case,
build the smallest faithful stand-in that still exercises the real code path
end to end (the real router, the real handlers, a real connection to a real
or realistic database) rather than skipping verification. The goal is
observing the real code execute, not observing a mock of it.

## Reversibility is part of verification, not separate from it

Any data written purely to make a verification pass possible must be cleaned
up in the same pass, before reporting success — and the cleanup itself
should be confirmed (re-query and check the row count), not assumed. See
[`METHODOLOGY.md`](../METHODOLOGY.md#4-core-principles), principle 4.

## Reporting

A verification report states the claim being checked, exactly how the
service was reached (what was actually running), each request sent and the
response captured, and — critically — at least one negative or adversarial
case, not just the happy path. A report that's all happy-path is a replay of
the spec, not a verification of it.

## Tooling to close the gaps (validated, not invented)

An honest audit against the IBM API-testing taxonomy found gaps this
methodology didn't cover with a concrete tool — not principles, actual
tools, checked against real GitHub activity:

- **Automated regression, when a project can support one**: **Vitest**,
  split `tests/unit/` (pure logic) and `tests/integration/` (real server +
  real DB via `fetch`, no mocks — same "real HTTP to a real port"
  principle as manual VERIFY, just repeatable). See
  `examples/harness-substrate/tests/` for the pattern and
  `docs/07-spec-driven-development.md`'s "Unit vs. integration" section for
  which one a given `R<n>` needs.
  Node's built-in `node:test` was the first choice here (zero extra
  dependency) but was replaced after checking
  [the primary source](https://nodejs.org/api/test.html) directly: only
  `test()`/`describe()`/`it()`/hooks are "Stability: 2 — Stable" in
  `node:test`. Everything a real verification flow actually leans on —
  coverage (`--experimental-test-coverage`), watch mode (`--watch`), module
  mocking (`mock.module`) — is explicitly flagged "Stability: 1 —
  Experimental" or "1.0 — Early development" by Node.js itself. Vitest's
  equivalents (coverage, watch, mocking) are stable and more mature. Verify
  this claim yourself against the docs before trusting it secondhand — it's
  a point-in-time reading of a page that changes with each Node release.
  Projects without an established test culture (most real API projects
  this harness governs today) are not required to adopt this —
  Thunder-Client-style manual cases stay valid, see
  [`docs/07-spec-driven-development.md`](07-spec-driven-development.md).
- **Machine-checkable contract**: [`express-openapi-validator`](https://github.com/topics/contract-testing)
  — validates real requests/responses against an OpenAPI file at runtime,
  turning `requirements.md`'s EARS requirements into an enforced schema
  instead of prose a human has to eyeball. See
  `examples/harness-substrate/openapi.yaml` and the wiring documented in
  that substrate's `PROJECT-CONVENTIONS.md`.
- **Security battery, traced to a standard**: the security battery above
  now maps onto the [OWASP API Security Testing Framework](https://github.com/OWASP/www-project-api-security-testing-framework)
  (100% coverage of the OWASP API Security Top 10 2023, plus specific JWT
  attack cases: `none` algorithm, RS256→HS256 confusion, `kid` path
  traversal) — cite it instead of maintaining this list from memory alone.
- **Load/stress** (previously an open gap, not covered at all): `autocannon`
  (Node-native, zero setup, run against the same temporary server VERIFY
  already spins up) for quick checks; [`k6`](https://github.com/grafana/k6)
  (30k+ stars, the most-adopted option) if a project ever needs real CI/CD
  load testing. Neither is wired into any checkpoint by default — add it
  per-project only when traffic volume is an actual concern, per the same
  "don't pay for what you don't need" principle as the review fan-out.
- **Not adopted, and why**: interoperability testing (multiple
  protocols/formats) doesn't apply to a single-format JSON/HTTP stack — no
  tool was force-fit here. Shift-right/post-production monitoring
  (SigNoz, Uptrace, Jaeger — all real, OpenTelemetry-native, self-hosted)
  needs actual running infrastructure, not a package install; it's a real
  gap, left open, not silently declared "covered."
