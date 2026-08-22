# progress/

Persistent, on-disk state for the harness — the "Memory & State" primitive
from `METHODOLOGY.md` section 5. Nothing in here is reconstructed from
conversation memory; it's read from disk at the start of every cycle and
written to disk at the end of every stage. See `AGENTS.md` for who writes
what.

- `current.md` — the active session's approved plan. One at a time,
  overwritten on the next PLAN stage. Its content at the moment a cycle
  finishes should be copied into `history.md` before it's overwritten.
- `history.md` — append-only. Never edit a past entry; append a correction
  as a new dated entry instead.
- `impl_<feature-id>.md` — one per feature, written by `harness-implementer`.
  Not created until that feature has an approved plan.
- `review_<feature-id>.md` — one per feature, written by `harness-reviewer`.

`<feature-id>` matches the `id` field in `feature_list.json`.
