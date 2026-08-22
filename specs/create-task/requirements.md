# requirements.md — create-task

> Feature `create-task` de `feature_list.json` (`"sdd": true`, status
> `pending` al momento de redactar este spec). Notación EARS estricta —
> ver `.claude/agents/spec_author.md`.

## Contexto investigado (precedente real)

- No hubo `progress/explore_create-task-*.md` provisto por el leader — se
  investigó directo el código de `examples/harness-substrate/src/`.
- Precedente de endpoint: `GET /api/tasks` (`src/routes/tasks.js` →
  `src/controllers/tasks.js` `getAll()`). Mismo router (`src/routes/tasks.js`
  existente, un solo archivo para todo el recurso `tasks`), mismo
  controlador (`src/controllers/tasks.js`), mismo modelo (`src/models/task.js`,
  `modelName: 'Task'`, `tableName: 'tasks'`, columnas `id` (PK autoincrement),
  `title` (`STRING(200)`, `allowNull: false`), `done` (`BOOLEAN`,
  `allowNull: false`, `defaultValue: false`)).
- `src/utils/validate.js` ya contiene `isValidTitle(title)` — función pura
  (`typeof title === 'string' && title.length >= 1 && title.length <= 200`)
  con un comentario explícito dejado para esta feature: "Cuando la feature
  create-task se implemente vía el flujo SDD real (spec_author ->
  implementer), esto es lo que un Joi schema envolvería". El design.md se
  apoya en esa función existente, no la reemplaza.
- `PROJECT-CONVENTIONS.md` confirma la capa de 3 niveles
  (routes/validators/controllers) y que Joi **no está instalado todavía**
  ("add as a dependency the first time a validator is written").
- `openapi.yaml` documenta hoy solo `GET /health` y `GET /api/tasks` — no
  tiene `POST /api/tasks/create`. Queda fuera del alcance de este spec
  actualizarlo (no es parte del `acceptance` de la feature); se anota como
  gap conocido en `design.md`.
- Test strategy real: Vitest, `tests/unit/` y `tests/integration/`
  (`package.json` scripts `test`, `test:unit`, `test:integration`). Hay
  precedente exacto de ambos: `tests/unit/validate.test.js` (unit puro
  sobre `isValidTitle`) y `tests/integration/tasks.test.js` (servidor real
  + sqlite real + `fetch`, sin mocks).

## Requirements

**R1.** CUANDO llega `POST /api/tasks/create` con un `title` string de
1 a 200 caracteres en el body, el sistema DEBE responder con status HTTP
200 y cuerpo `{status: true, data: {...}}` donde `data` es la fila creada
en la tabla `tasks`.

**R2.** SI el body de `POST /api/tasks/create` no incluye el campo
`title`, o `title` es una cadena vacía, ENTONCES el sistema DEBE responder
`{status: false, error: <mensaje>}` sin crear ninguna fila en la tabla
`tasks`.

**R3.** MIENTRAS el campo `done` esté ausente del body de
`POST /api/tasks/create`, el sistema DEBE persistir la fila creada con
`done = false` (booleano, nunca `null`).

**R4.** El sistema DEBE construir en `src/controllers/tasks.js` el objeto
pasado a `models.Task.create()` campo por campo (`{title: ..., done: ...}`),
sin reenviar el objeto `req.body`/`data` crudo recibido de la capa HTTP.

**R5.** SI `title` excede 200 caracteres o no es de tipo string, ENTONCES
el sistema DEBE responder `{status: false, error: <mensaje>}` sin crear
ninguna fila en la tabla `tasks`.

> R5 no está en el `acceptance` literal de `feature_list.json`, pero es
> una consecuencia directa e inequívoca de "title es requerido, 1-200
> caracteres" en la `description` de la feature y de la función
> `isValidTitle` ya existente en `src/utils/validate.js` (que ya cubre
> longitud, no solo ausencia). Se incluye para no dejar un hueco de
> validación a medio construir sobre una función que ya prueba ese caso
> (`tests/unit/validate.test.js` ya tiene el caso "rechaza más de 200
> caracteres"). No inventa comportamiento nuevo — formaliza como
> requirement lo que el precedente ya implementa y testea.

## Trazabilidad — `acceptance` original → `R<n>`

| # | `acceptance` (feature_list.json)                                                              | Cubierto por |
|---|---------------------------------------------------------------------------------------------|--------------|
| 1 | POST /api/tasks/create con title válido responde {status:true, data:{...}} con la fila creada | R1           |
| 2 | title ausente o vacío responde {status:false, error:...} sin tocar la DB                      | R2           |
| 3 | done omitido persiste como false en la DB (no null)                                            | R3           |
| 4 | src/controllers/tasks.js construye el objeto pasado a .create() campo por campo, sin reenviar req.body crudo | R4 |
| — | (derivado de la description: "1-200 caracteres")                                              | R5           |
