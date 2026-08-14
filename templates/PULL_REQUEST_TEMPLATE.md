<!--
This is the artifact that makes the LEARN stage (docs/06) a real, visible
step in an actual DevOps PR flow — not just something an agent is trusted
to remember on its own. Copy this into .github/PULL_REQUEST_TEMPLATE.md
(GitHub) or your platform's equivalent (Azure DevOps, GitLab, etc.) so
every PR carries it, regardless of who or what opened the PR.

The scenario this is built for: a junior engineer (or an agent working on
a junior engineer's behalf) opens a PR. A tech lead reviews it — possibly
across several rounds of comments. The PR eventually gets approved and
merged. This template makes sure the LAST thing that happens before merge
is an explicit answer to "did anything from this review round need to
survive past this PR," instead of that question only ever getting asked
informally, inconsistently, or not at all.
-->

## What this PR does

<One paragraph. Link the ticket/spec if there is one.>

## Verification

<Paste the actual verification evidence — real requests, real responses,
per docs/03-runtime-verification.md. Not "tests pass." Not "looks correct.">

## Review checklist (fill in before requesting the final approval)

- [ ] Multi-agent / independent review pass run on this diff (docs/02)
- [ ] Every negative/edge case in the standard battery was actually sent,
      not just reasoned about (docs/03)
- [ ] Every test fixture written during verification was cleaned up and the
      cleanup was confirmed, not assumed

## Before merging: did anything from this review round need to be captured?

<This is the LEARN stage (docs/06), made explicit and impossible to skip
silently. Answer honestly — "none of the above" is a valid, complete
answer; leaving this section blank is not.>

- [ ] **A reviewer correction that will recur** on future PRs (a style rule,
      an architectural convention, a "we don't do X here and here's why") →
      added to `PROJECT-CONVENTIONS.md` under "Recurring reviewer
      conventions," dated. **Paste the diff of that addition here:**

  ```diff

  ```

- [ ] **A reviewer confirmation of an unusual choice** (something that looks
      wrong at a glance but was deliberately approved) → same section, same
      treatment — a confirmation prevents the *next* person from "fixing"
      a decision that was already made on purpose.

- [ ] **A bug class specific to this stack**, not a one-off typo → captured
      as a `lesson` memory (see `templates/memory-entry-examples/lesson-example.md`),
      not just fixed inline.

- [ ] **A deliberate, reviewed tradeoff** that a future PR shouldn't
      silently "fix" (e.g. a known race condition, accepted for now) →
      added to `PROJECT-CONVENTIONS.md` under "Known gaps / accepted
      tradeoffs."

- [ ] None of the above applied to this review round.

<!-- Reviewer: if you left a comment that falls into any of the categories
above and the PR author didn't check the corresponding box, ask them to
before approving. This checklist has no teeth if it's only ever
self-reported without the reviewer holding it to account — same as any
other review checklist. -->
