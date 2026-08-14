---
name: lesson_example-slug
description: One-sentence summary of the mistake and its corrective rule.
metadata:
  type: lesson
  confidence: high | medium | low
  status: active   # active | retired | superseded-by-<name>
  createdAt: YYYY-MM-DD
  lastValidated: YYYY-MM-DD
---

**What happened:** A factual, one-to-three-sentence account of the mistake.
Be specific about the trigger — what input, state, or assumption caused it.

Example: "Assumed a shared `findActiveChildById`-style helper filtered on
every status flag the caller cared about. It only filtered the child
table's own flags, not the parent's — so a soft-deleted or archived parent
record could still pass the check."

**Why it happened:** The root cause, not the symptom. Usually: an assumption
that turned out to be false, or a check that looked like a superset of an
older check but wasn't.

**How to avoid:** The concrete rule the next session should follow. Should
be specific enough to act on directly, not a vague "be careful."

**Detection signal:** How a future session recognizes it's about to repeat
this — a pattern to watch for, a question to ask before proceeding.

Related: [[another-memory-slug]]
