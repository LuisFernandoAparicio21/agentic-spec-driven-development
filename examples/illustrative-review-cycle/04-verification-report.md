# Example verification report: POST /api/widgets/create

**Verdict:** PASS (after one fix applied — see step 3)

**Claim:** Creates a widget for an active owner; rejects invalid/missing
fields and nonexistent owners with specific messages.

**Method:** Local instance of the service running against a real (staging)
database. Requests sent via `curl`.

## Steps

1. ✅ Happy path — valid `owner_id`, `label`, `quantity` → `{"status":true}`,
   HTTP 200. Confirmed the row exists in the DB with the exact values sent.
2. 🔍 `quantity: 2.5` → **initially accepted** (see review finding above) —
   fixed by adding `.integer()` to the Joi rule, re-verified: now correctly
   rejected with `"quantity" must be an integer`.
3. 🔍 Missing `owner_id` → `{"status":false,"error":"\"owner_id\" is
   required"}`.
4. 🔍 Nonexistent `owner_id` (999999) → `{"status":false,"error":"owner_id
   does not exist"}`.
5. 🔍 `label` at 101 characters → correctly rejected with the length
   message.
6. 🔍 SQL-injection-shaped string in `label`
   (`'; DROP TABLE widgets;--`) → accepted and stored as inert literal
   text; table confirmed intact afterward.
7. 🔍 15 concurrent identical requests → all 15 succeeded independently (no
   uniqueness constraint applies to this endpoint by design), no crash, no
   duplicate-detection expected or observed.
8. ✅ Cleanup — all rows created during this pass deleted, row count
   confirmed back to baseline before reporting success.

## Findings

- ⚠️ Step 2 caught a real gap the plan didn't anticipate (`quantity`
  accepting non-integers) — fixed and re-verified before shipping, not just
  noted for later.
- No other adjacent issues surfaced during the negative-case battery.
