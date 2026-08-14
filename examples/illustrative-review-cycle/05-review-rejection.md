# Example: review sends the widgets diff back

> Continuation of the invented `widgets` example. Two comments came back on
> the same diff — one functionality, one readability/convention.

## Comment 1 (functionality) — specific to this field

> "`label` is validated with `.min(1)` *before* it gets trimmed in the
> controller. Send `"   "` (three spaces) — it passes validation (length 3
> ≥ 1), then `controllers/widgets.js` trims it to `""` before storing. You
> can create a widget with an empty label."

**Verified by reproducing it:** sent `{"owner_id":1,"label":"   ","quantity":1}`
→ `{"status":true}` → stored row has `"label": ""`. Confirmed, this is real.

**Fix:** validate the *trimmed* value, not the raw one — `Joi.string().trim().min(1).max(100)`
(Joi's `.trim()` transform runs before `.min()`/`.max()` evaluate the
length, so this closes the gap in one change, in the validator, without
touching the controller).

**Scope judgment:** this is specific to *this field's* trim-then-store
pattern. Other fields on other resources that don't get trimmed aren't
affected by the same gap. → captured as a narrow **lesson**, not a
project-wide convention (see `06-captured-convention.md`).

## Comment 2 (readability/convention) — a repeat of something said before

> "Error messages here leak Joi's internal field-path noise —
> `'owner_id does not exist (owner_id)'` reads like a bug, not an intentional
> message. Strip the path suffix in the shared validator response wrapper so
> every validator's error messages are clean by default, not just this one."

This is the **second time** this same comment has been made on this
project — it was also raised on the `gadgets` PR, fixed there in isolation,
and never generalized. That means the next resource after `widgets` would
hit it a third time.

**Fix:** rather than stripping the suffix in each validator individually
(which is what happened both previous times), fix it once in the shared
response-shaping wrapper every validator already calls, so it can't recur
per-resource again.

**Scope judgment:** this is exactly the case
[`docs/06-review-feedback-to-durable-convention.md`](../../docs/06-review-feedback-to-durable-convention.md)
describes — a pattern that already recurred once and was about to recur
again. → captured as a durable **project convention**, not just fixed
locally (see `06-captured-convention.md`).
