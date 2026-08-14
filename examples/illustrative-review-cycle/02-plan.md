# Example plan: POST /api/widgets/create

> Continuation of the invented `01-spec.md` example.

## Precedent found

`POST /api/gadgets/create` (`routes/gadgets.js` + `validators/gadgets.js` +
`controllers/gadgets.js`) solves the same shape of problem: a single
required FK to an "owner"-like parent, plus scalar fields, no nested arrays.
Mirroring its structure directly.

## Files to change

- **`src/routes/widgets.js`** (new) — `POST /create` route. Calls the
  validator, then the controller, shapes the JSON response. No direct DB
  access, matching the existing pattern in `routes/gadgets.js`.
- **`src/validators/widgets.js`** (new) — `createValidator(data)`. Joi
  schema with `owner_id`, `label`, `quantity`. `owner_id` gets a field-level
  `.external()` existence check reusing `ownersController.findById` (already
  exists — **do not** write a new lookup).
- **`src/controllers/widgets.js`** (new) — `create(data)`. Builds the
  Sequelize `.create()` call explicitly field by field, matching
  `controllers/gadgets.js`'s `create()` shape.

## Reused, not reimplemented

- `ownersController.findById` — existing FK-existence check, already
  filters on the owner's active/soft-deleted status. No new lookup needed.
- `utils/response.js`'s existing `{status, error}` response shaping,
  already used by every sibling route.

## Validation rules and exact messages

| Rule | Message |
|---|---|
| `owner_id` missing | `"owner_id" is required` (Joi default) |
| `owner_id` doesn't exist / inactive | `owner_id does not exist` |
| `label` missing or empty | `"label" is required` (Joi default) |
| `label` over 100 chars | `"label" length must be less than or equal to 100 characters long` (Joi default) |
| `quantity` missing | `"quantity" is required` (Joi default) |
| `quantity` negative | `"quantity" must be greater than or equal to 0` (Joi default) |

## Verification plan

- Happy path against a real owner.
- Missing `owner_id`, nonexistent `owner_id`, inactive `owner_id`.
- `label` empty, `label` at 101 chars.
- `quantity` negative.
- SQL-injection-shaped string in `label` — confirm stored as literal text.
- 15 concurrent identical requests — confirm no duplicate-row or crash
  behavior, since `owner_id` + `label` has no uniqueness constraint being
  tested here but the concurrency battery is run regardless, per the
  methodology's default battery.
