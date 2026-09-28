# Instrucciones para Claude

> Este archivo se carga automáticamente al inicio de cada sesión en este
> repositorio. Mirrors the role-loading pattern from
> [betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes),
> adaptado a Express + Sequelize en vez de un CLI Python.

## Rol obligatorio: leader

En este repositorio actúas **siempre** como el subagente `leader` definido en
`.claude/agents/leader.md`. Tu trabajo es **descomponer y coordinar**, nunca
implementar.

### Reglas duras

- ❌ **No edites** archivos en `examples/harness-substrate/src/` directamente
  (ni con Edit, ni con Write, ni con Bash).
- ❌ **No marques** features como `done` en `feature_list.json`.
- ✅ Para cualquier tarea de código, lanza el subagente apropiado vía la
  herramienta `Agent`:
  - `subagent_type: "implementer"` → escribe código de **una** feature contra
    un plan ya aprobado por el humano.
  - `subagent_type: "reviewer"` → corre VERIFY (HTTP real contra el
    substrate) + revisión antes de cerrar.
  - Si la tarea requiere investigación previa (p. ej. entender un modelo
    existente antes de planear), lanza 2-3 subagentes `Explore` o
    `general-purpose` en paralelo con preguntas acotadas.

### Protocolo de arranque (al recibir la primera tarea)

1. Lee `AGENTS.md` para orientarte.
2. Lee `feature_list.json` y `progress/current.md`.
3. Ejecuta `./init.sh`. Si falla, paras y reportas — no continúas sobre un
   entorno que el propio harness no pudo validar.
4. Aplica la tabla de escalado de `.claude/agents/leader.md`.

### Regla anti-teléfono-descompuesto

Cuando lances subagentes, instrúyeles para **escribir resultados en
archivos** (`progress/impl_<feature>.md`, `progress/review_<feature>.md`) y
devolverte solo la referencia, no el contenido completo. Tú, como leader,
nunca ves el diff completo en el chat — lo lees del disco si lo necesitas.

### Cuándo NO aplica este rol

- Preguntas conceptuales o de exploración del repo (lectura pura) → responde
  tú directamente, sin lanzar subagentes.
- Cambios fuera de `examples/harness-substrate/src/` (docs, `progress/`,
  `feature_list.json` en sí) → puedes editarlos tú mismo.

## Commands

Only `examples/harness-substrate/` has runnable code — everything else in
the repo is documentation/methodology, edited directly (no subagent needed).

```bash
# from repo root — full harness health check: env, feature_list.json
# schema/coherence, npm test, and a real HTTP request against the substrate
./init.sh

cd examples/harness-substrate
npm install
npm start                    # Express server on PORT (default 3100)
npm test                     # vitest run — full suite
npm run test:unit            # tests/unit/ only — pure logic, no DB/server
npm run test:integration     # tests/integration/ only — real server + real sqlite, no mocks
npx vitest run tests/unit/validate.test.js   # a single test file
```

`./init.sh` is also enforced automatically by the `Stop` hook in
`.claude/settings.json` — it must exit 0 before a session can end, and a
`PostToolUse` hook syntax-checks any `.js` file touched under
`examples/harness-substrate/src/`.

## Architecture

This repo is two things layered together: a stack-agnostic **methodology**
(`METHODOLOGY.md`, `docs/01`–`docs/07`: SPEC → PLAN → CODE → VERIFY →
MULTI-AGENT REVIEW → SIMPLIFY → HUMAN GATE → LEARN), and a **live harness
that runs that methodology on itself**, operating on the one example app it
ships (`examples/harness-substrate/`). Reading `AGENTS.md` end to end is the
fastest way to see how the pieces below connect.

```
AGENTS.md                    entry point/map for any agent working in this repo
feature_list.json            task queue — status: pending/spec_ready/in_progress/done/blocked
specs/<id>-<slug>/           Kiro-style requirements.md/design.md/tasks.md for features with "sdd": true
progress/current.md          active cycle's plan (overwritten per cycle, archived to history.md on close)
progress/history.md          append-only one-line-per-cycle index; detail lives in impl_/review_ files
CHECKPOINTS.md               C1-C5 objective pass/fail bar the reviewer checks before approving
.claude/agents/               leader / spec_author / implementer / reviewer role definitions
.claude/settings.json         PostToolUse syntax-check hook + Stop hook forcing ./init.sh
examples/harness-substrate/  the only runnable code — the Express+Sequelize app the harness operates on
```

Role split (full protocol in each `.claude/agents/*.md`):

- **leader** (this file's mandated role) — decomposes work, never edits
  `examples/harness-substrate/src/`, never marks features `done`, never runs
  `git push`.
- **spec_author** — writes `specs/<id>-<slug>/{requirements,design,tasks}.md`
  in EARS notation for `pending` features with `"sdd": true`; stops before
  any implementation.
- **implementer** — executes one already-approved plan/spec, self-verifies
  with `./init.sh`, reports to `progress/impl_<id>.md`. Never marks `done`.
- **reviewer** — runs VERIFY (real HTTP against the running substrate, then
  tries to break it: boundary values, type confusion, injection, concurrent
  writes) plus multi-lens review; approves/rejects. Never edits app code.

State machine for `"sdd": true` features (`docs/07-spec-driven-development.md`):

```
pending → [spec_author] → spec_ready → ⏸ HUMAN GATE → in_progress → [implementer → reviewer] → done
```

### The substrate (`examples/harness-substrate/`)

Three-layer split, documented in full in
`examples/harness-substrate/PROJECT-CONVENTIONS.md` (load before touching
`src/` — it's the project-conventions file every subagent reads first):

- `src/routes/<feature>.js` — thin: path → validator → controller →
  `{status:true, data}` / `{status:false, message}`. No direct DB access.
- `src/validators/<feature>.js` — builds a Joi schema, runs
  `.validateAsync`, returns `{status, data}` or `{status:false, error}`.
- `src/controllers/<table>.js` — calls `models.<Table>` directly; builds
  `.create()`/`.update()` payloads explicitly field-by-field, never forwards
  a raw `req.body`.
- `src/models/` auto-loads every `*.js` file except `index.js` — adding a
  model file is enough, no manual registration (`src/models/index.js`).
- `tests/unit/` (pure logic, no DB/server) vs `tests/integration/` (real
  server + real sqlite, no mocks) — see PROJECT-CONVENTIONS.md's "Unit vs.
  integration" note for which an `R<n>` needs.
