# Project Conventions — harness-substrate

<!--
Filled-in instance of ../../templates/PROJECT-CONVENTIONS.md.template for
this specific substrate. Loaded in full by every agent role before touching
code — see AGENTS.md. Append to this file (don't rewrite it) as LEARN
stages confirm new conventions.
-->

## Stack

- Framework: Express 4
- ORM / DB driver: Sequelize 6 over sqlite (file-based, `substrate.sqlite`
  at the package root, gitignored)
- Validation library: Joi (add as a dependency the first time a validator is
  written — not pre-installed, since no feature has needed it yet)
- Test strategy: **Vitest**, split `tests/unit/` (pure logic, no DB, no
  server — e.g. `tests/unit/validate.test.js`) and `tests/integration/`
  (real server + real sqlite + real `fetch`, no mocks — e.g.
  `tests/integration/tasks.test.js`). See
  `docs/07-spec-driven-development.md`'s "Unit vs. integration" section for
  which one a given `R<n>` needs. Run everything with `npm test`, or split
  with `npm run test:unit` / `npm run test:integration`. This replaces "no
  automated suite" now that the substrate has real endpoints worth
  regression-testing; `smapp_backend` and other real projects without an
  established test culture are not required to adopt this yet — see
  `docs/03-runtime-verification.md`'s "Tooling to close the gaps" section.
  (Earlier version of this substrate used bare `node:test` — kept the same
  "real HTTP, no mocks" principle, switched to Vitest for the unit/
  integration split and nicer DX.)

## Commands

```
cd examples/harness-substrate
npm install
npm start            # listens on PORT, default 3100

# from the repo root, not here:
./init.sh             # checks the harness itself, starts this server,
                       # curls /health, stops it — the minimal proof VERIFY
                       # tooling actually works
```

## Architecture: the API layer

- `src/routes/<feature>.js` — thin. Defines paths, calls the validator, calls
  the matching controller, shapes the HTTP response as
  `{status:true, data:...}` or `{status:false, message:...}`. No direct
  database access.
- `src/validators/<feature>.js` — exports async functions that build a Joi
  schema, run `.validateAsync`, and return `{status, data}` on success or
  `{status:false, error:message}` on failure.
- `src/controllers/<table>.js` — plain async functions that call
  `models.<Table>` directly. Build the object passed to `.create()` /
  `.update()` explicitly, field by field — never forward a raw
  `req.body`/`data` object into a write call.
- `src/models/` auto-loads every `*.js` file except `index.js` — adding a
  model file is enough, no manual registration. See `src/models/index.js`.

## Contrato machine-checkable (express-openapi-validator)

`openapi.yaml` (repo root of this substrate) is the real contract backing
`specs/<id>/requirements.md`'s EARS requirements — see
`docs/01-planning-phase.md`'s "stronger SPEC" section. Wiring it into
`app.js` as request/response validation middleware:

```javascript
const { OpenApiValidator } = require('express-openapi-validator');
// after app.use(express.json()), before mounting routers:
app.use(
  OpenApiValidator.middleware({
    apiSpec: './openapi.yaml',
    validateResponses: true
  })
);
```

**Status: written, not yet verified running.** `express-openapi-validator`
is listed in `devDependencies` but this sandbox has no network for
`npm install`, so this snippet is not wired into `app.js` yet — adding
unverified middleware to the one thing `init.sh` actually exercises would
violate the harness's own VERIFY principle. Whoever runs `npm install`
with real network should wire this in, run `./init.sh`, confirm it still
passes, and only then move this snippet from "documented" to "in `app.js`."

## Recurring reviewer conventions

<!-- Appended here by harness-leader during LEARN, one entry per confirmed
convention, each traceable to a specific cycle's progress/review_*.md. -->

_(none captured yet — this file grows as cycles run)_

## Known gaps / accepted tradeoffs

_(none yet)_

## Database reality check

`substrate.sqlite` is created fresh by `sequelize.sync()` on server start —
unlike a real project, there is no drift risk here between migrations and
live schema, because there are no migrations; models are the only source of
truth for this substrate's schema.
