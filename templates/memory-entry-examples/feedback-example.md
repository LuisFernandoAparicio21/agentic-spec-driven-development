---
name: feedback_example-slug
description: One-line summary of the corrected or confirmed approach.
metadata:
  type: feedback
  confidence: high
  status: active
  createdAt: YYYY-MM-DD
---

Lead with the rule itself, stated as an instruction for the future, not a
narration of what happened.

Example: "Validator catch blocks return `{status:false, error:message}`,
never `{status:false, message}` — the property is named `error` so the
route doesn't have to remap it."

**Why:** The reasoning the reviewer gave — often tied to a past incident or
a strong, stated preference. This is what lets a future session judge edge
cases the rule itself doesn't explicitly cover.

**How to apply:** When/where this kicks in. Be specific about scope — a
correction given about one file is not automatically a project-wide rule
unless the human said so.

<!-- Confirmations matter as much as corrections. If a human validated an
unusual choice without pushback ("yes, that's right, keep doing that"),
record it the same way — it stops a future session from "fixing" something
that was already a deliberate, approved decision. -->

Related: [[another-memory-slug]]
