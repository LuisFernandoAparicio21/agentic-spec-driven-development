# History

Append-only log of durable decisions, captured rules, and cycle outcomes.
Never edit a past entry — append a correction as a new dated entry that
references it. See `docs/06-review-feedback-to-durable-convention.md` for
what belongs here versus in
`examples/harness-substrate/PROJECT-CONVENTIONS.md`.

Format per entry — **one line, pointing at the detail file that already
has it** (`progress/impl_<id>.md` / `progress/review_<id>.md`). This file
is append-only and never trimmed; a full paragraph per entry gets
expensive to read after enough cycles. See
`.claude/agents/leader.md`'s "Cómo escribir en progress/history.md":

```
## <YYYY-MM-DD> <feature-id> — <one-line hook>
Detail: progress/review_<feature-id>.md
```

<!-- Entries start below. -->
