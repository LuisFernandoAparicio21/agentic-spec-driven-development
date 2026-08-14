# Planning Phase

## Purpose

Turn an ambiguous request ("add an endpoint to update X") into a reviewable,
file-level plan before a single line of implementation code exists.

## Trigger

Enter the planning phase whenever a request:

- adds a new endpoint (any new route),
- changes the shape of an existing request or response,
- touches more than one file, or
- has more than one reasonable way to implement it.

Skip it only for genuinely trivial, single-line, unambiguous changes.

## What the agent does

1. **Research the closest precedent.** Before proposing anything new, search
   the codebase for a sibling endpoint that already solves a structurally
   similar problem (same HTTP method, similar body shape, similar validation
   needs). Read it in full — route, validator, and controller. This is the
   single highest-value research step: a codebase that already has 30
   endpoints has almost certainly already solved your problem's shape once.
2. **Identify what's reusable.** Name the specific existing helper functions,
   validation patterns, and utilities that the new endpoint should call
   instead of reimplementing. A new endpoint that doesn't reuse anything from
   an already-solved sibling is a signal something was missed in research,
   not a sign of a genuinely novel problem.
3. **Resolve ambiguity with the human, not by guessing.** If the spec doesn't
   say whether an update is a partial patch or a full replace, whether a
   field is required, or what happens on a duplicate — ask. A plan built on
   a guessed assumption just moves the cost of that guess later, where it's
   more expensive to unwind.
4. **Write the plan as a concrete artifact**, naming:
   - the exact files to create or modify,
   - the request/response shape,
   - the validation rules and their exact rejection messages,
   - which existing functions get reused, verbatim (with their real
     signatures) — not paraphrased,
   - how the change will be verified once implemented.
5. **Stop and wait for approval.** The plan is not a formality — it's the
   cheapest point in the whole loop to redirect. Do not begin implementation
   until a human has explicitly approved the plan or asked for changes to
   it.

## What "good" looks like

A good plan names files and reused functions specifically enough that a
reviewer could sanity-check it without reading any code — "this validator
will call `usersController.findByEmail`, which already exists and does X" is
checkable in one sentence; "we'll validate the user" is not.

## What "bad" looks like

- A plan that describes behavior in the abstract ("add proper validation")
  without naming the actual rules.
- A plan that invents a new pattern where an existing, working one already
  covers the same shape of problem, without explaining why the existing one
  doesn't fit.
- Silently proceeding past an ambiguous requirement instead of surfacing the
  ambiguity as a question.

## Why the approval gate matters specifically here

Every stage downstream — implementation, review, verification — inherits
whatever the plan got wrong. A misunderstood requirement caught at the plan
stage costs a sentence of clarification. The same misunderstanding caught
after code, a multi-agent review pass, and a verification pass have all
already run against the wrong assumption costs all of that work, plus the
review/verify cycle has to run again.

## A stronger SPEC: contract-backed instead of prose-only

The SPEC described so far is a prose paragraph — enough for a human to
approve and an agent to implement against. For a project that wants the
contract itself to be machine-checkable (so a client can't drift from what
the server actually returns without a test failing), back the SPEC with a
real OpenAPI/JSON-schema definition instead of only prose, and let the
VERIFY stage include an automated contract-conformance check — the
response shape is diffed against the schema, not just eyeballed. This is
strictly additive to the workflow described here: the PLAN and CODE stages
don't change, VERIFY just gets one more, cheaper-to-run check alongside the
real HTTP requests. Worth adopting once a project has more than a handful
of endpoints and more than one consumer who can be broken by silent drift;
overhead not worth paying for a one-off internal endpoint with a single
caller.
