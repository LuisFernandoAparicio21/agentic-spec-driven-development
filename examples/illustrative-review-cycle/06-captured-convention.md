# Example: what gets written down after the review cycle

> Continuation of `05-review-rejection.md`. Two fixes shipped in the same
> follow-up commit; only one of them also produces a durable artifact,
> because only one of them was judged to be a recurring pattern rather than
> a one-off.

## The narrow fix — no durable artifact needed

The `label` trim-then-empty-string gap was specific to that one field's
validation order. It doesn't get a project-convention entry. It's
plausible — though not certain — that this exact shape of bug (validate
before a transform is applied) could recur on a different trimmed field
later; if it does recur once, *that's* the trigger to promote it from a
one-off fix to a lesson. Capturing every possible-but-unconfirmed pattern
as a durable rule on its first occurrence would flood the conventions file
with speculative entries — the discipline in
[`docs/04-memory-institutional-knowledge.md`](../../docs/04-memory-institutional-knowledge.md#what-makes-a-memory-worth-writing-down)
is to write conservatively, even though this doc's own stage exists to make
sure the *option* isn't skipped.

## The recurring pattern — captured as a durable project convention

This is the second time the same comment was made project-wide. Per
[`docs/06-review-feedback-to-durable-convention.md`](../../docs/06-review-feedback-to-durable-convention.md),
that's the trigger to stop fixing it locally and generalize it. Appended to
this project's conventions file:

```markdown
## Recurring reviewer conventions

- Validator error messages must not leak Joi's internal field-path suffix
  (e.g. `(owner_id)`) to the API consumer — strip it in the shared
  validator-response wrapper, not per-validator. Raised on both `gadgets`
  and `widgets`; fixed centrally this time so it can't recur on the next
  resource. <!-- learned: 2026-08-14 -->
```

And because the fix itself was structural (moved into a shared wrapper
rather than patched per-file), that wrapper change is exactly the kind of
thing worth a one-line note in the code itself too, per the "document
ad-hoc decisions in both code and durable memory" principle — not just in
the conventions file, so a future reader looking only at the wrapper
function still sees why it exists.

## What this demonstrates

The same review cycle produced two different outcomes because the two
comments were different *kinds* of finding — one bound to a specific
field's specific behavior, one bound to a pattern already proven to recur
across resources. Treating both the same way (either persisting everything,
or persisting nothing) would be wrong in one direction or the other. The
LEARN stage's job is making that judgment call explicit and deliberate
instead of defaulting to whichever one is easier to skip.
