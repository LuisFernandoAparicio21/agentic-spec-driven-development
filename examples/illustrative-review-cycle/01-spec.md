# Example spec: POST /api/widgets/create

> This is a fully generic, invented example used to illustrate the format of
> each artifact in the workflow. It is not derived from any real project.

**Method:** POST
**URL:** `/api/widgets/create`

**Params:**
- `owner_id` (int, required, min 1) — must reference an existing, active
  owner.
- `label` (string, required, 1–100 chars).
- `quantity` (int, required, min 0).

**Response on success:**
```json
{ "status": true }
```

**Response on validation failure:**
```json
{ "status": false, "error": "<specific message>" }
```

**Ambiguity resolved before planning began:** the spec as given didn't say
whether `owner_id` referring to a soft-deleted owner should be rejected.
Resolved with the requester: yes, reject — same rule already used by every
other "create" endpoint in this codebase for FK existence checks.
