# tasks.md — create-task

> El implementer marca `[x]` al completar cada paso. El reviewer rechaza
> si queda algún `[ ]` sin justificación documentada en `progress/impl_create-task.md`.

- [ ] 1. Agregar `joi` a `dependencies` en `examples/harness-substrate/package.json`
      y correr `npm install` dentro de `examples/harness-substrate/`. Confirmar
      que `node_modules/joi` existe antes de continuar. — (soporta R1, R2, R5)

- [ ] 2. Crear `examples/harness-substrate/src/validators/tasks.js` con
      `createValidator(data)`: schema Joi (`title` string requerido
      1-200 chars, `done` boolean con `.default(false)`), `validateAsync`,
      retorno `{status:true, data}` / `{status:false, error: err.message}`
      en catch — ver forma exacta en `design.md`. — (R1, R2, R3, R5)

- [ ] 3. Editar `examples/harness-substrate/src/controllers/tasks.js`:
      agregar `create(data)` que llama `models.Task.create({title: data.title, done: data.done})`
      campo por campo (nunca `data` crudo). Exportarla junto a `getAll`. — (R1, R3, R4)

- [ ] 4. Editar `examples/harness-substrate/src/routes/tasks.js`: agregar
      `router.post('/create', ...)` que llama `tasksValidator.createValidator(req.body)`,
      responde 400 + `{status:false, error}` si falla, o llama
      `tasksController.create(validation.data)` y responde
      `{status:true, data:task}` si pasa. Sin try/catch adicional
      alrededor de la llamada al controlador (ver design.md). — (R1, R2, R5)

- [ ] 5. **Unit test** — editar
      `examples/harness-substrate/tests/unit/validate.test.js` o crear
      `examples/harness-substrate/tests/unit/tasks-validator.test.js`
      (preferido: archivo nuevo, ya que prueba el validador Joi, no
      `isValidTitle` directamente) con casos: title válido → `status:true`
      con `data.done === false` por default; title ausente → `status:false`;
      title vacío → `status:false`; title > 200 chars → `status:false`;
      title no-string → `status:false`; `done:true` explícito se preserva
      en `data.done`. Sin DB, sin servidor — solo `createValidator()`
      llamado directo. — (R2, R3, R5)

- [ ] 6. **Integration test** — editar
      `examples/harness-substrate/tests/integration/tasks.test.js`,
      agregar `describe('POST /api/tasks/create', ...)` con casos:
      (a) `fetch` POST con `{title:'comprar pan'}` → 200,
      `body.status === true`, `body.data.title === 'comprar pan'`,
      `body.data.done === false`, y fila verificada en
      `db.Task.findByPk(body.data.id)`; (b) POST con `{}` (sin title) →
      `body.status === false`, verificar con `db.Task.count()` que no
      subió tras la llamada; (c) POST con `{title:''}` → mismo patrón que
      (b); (d) POST con `{title:'a'.repeat(201)}` → `body.status === false`,
      sin fila creada. Servidor real + sqlite real vía `beforeAll`/
      `beforeEach` ya existentes en el archivo — no mocks. — (R1, R2, R3, R5)

- [ ] 7. Verificación final: correr `./init.sh` desde la raíz del repo y
      confirmar que termina sin errores. Correr adicionalmente
      `npm test` dentro de `examples/harness-substrate/` (o
      `npm run test:unit` / `npm run test:integration` por separado) y
      pegar la salida real (verde, con conteo de tests pasados) en
      `progress/impl_create-task.md`, junto con la tabla de trazabilidad
      R1-R5 → archivo de test + nombre del `it(...)` que lo cubre. No
      marcar esta tarea `[x]` sin esa evidencia pegada. — (R1, R2, R3, R4, R5)
