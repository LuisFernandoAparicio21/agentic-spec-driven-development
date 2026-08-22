# design.md — create-task

## Archivos a crear/tocar

| Archivo                                                  | Acción | Motivo |
|-----------------------------------------------------------|--------|--------|
| `examples/harness-substrate/src/validators/tasks.js`       | Crear  | Nuevo — primer validador del proyecto. No existe carpeta `src/validators/` todavía; `PROJECT-CONVENTIONS.md` la describe pero ningún archivo la usa aún. |
| `examples/harness-substrate/src/routes/tasks.js`            | Editar | Agregar `router.post('/create', ...)` junto al `router.get('/', ...)` existente — mismo archivo de router para todo el recurso `tasks`, no uno nuevo. |
| `examples/harness-substrate/src/controllers/tasks.js`       | Editar | Agregar función `create(data)` junto a `getAll()` existente. |
| `examples/harness-substrate/package.json`                   | Editar | Agregar `joi` a `dependencies` — no está instalado (confirmado: no aparece en `dependencies` ni `devDependencies` actuales). Ejecutar `npm install joi` desde `examples/harness-substrate/`. |
| `examples/harness-substrate/tests/unit/validate.test.js` (o nuevo `tests/unit/tasks-validator.test.js`) | Crear/editar | Ver tasks.md — cubre R2/R5 vía el validador. |
| `examples/harness-substrate/tests/integration/tasks.test.js` | Editar | Agregar `describe('POST /api/tasks/create', ...)` junto al `describe('GET /api/tasks', ...)` existente — mismo archivo de integration test para el recurso `tasks`. |

`src/models/task.js` y `src/models/index.js` no se tocan — el modelo
`Task` ya tiene exactamente las columnas (`title`, `done` con
`defaultValue: false`) que esta feature necesita.

## Firmas nuevas

**`src/validators/tasks.js`**
```javascript
async function createValidator(data) { ... }
// retorna { status: true, data: { title, done } } en éxito
// retorna { status: false, error: <string> } en fallo
module.exports = { createValidator };
```

Construye un `Joi.object({ title: Joi.string().min(1).max(200).required(), done: Joi.boolean().default(false) })`,
corre `schema.validateAsync(data)`. El límite `min(1).max(200)` refleja
exactamente `isValidTitle` de `src/utils/validate.js` — no lo reemplaza,
lo formaliza en Joi (mismo criterio, dos capas: `isValidTitle` sigue
siendo la función pura unit-testeada, el schema Joi es la capa HTTP que
la envuelve, tal como el comentario dejado en `validate.js` anticipa).
`done` lleva `.default(false)` explícito en el lado Joi — mismo motivo que
la convención ya documentada para `smapp_backend` en `CLAUDE.md`
(booleanos opcionales que reflejan un `defaultValue` de columna necesitan
`.default(...)` en Joi, porque `undefined` todavía puede llegar a invocar
el setter de Sequelize según el motor/versión — más barato mantener la
regla aquí también que descubrir la diferencia por motor de DB en
producción).

Catch block: `return { status: false, error: err.message }` (forma
`error`, no `message`, tal como ya establece `PROJECT-CONVENTIONS.md` /
el equivalente confirmado en `smapp_backend`).

**`src/routes/tasks.js`** — agregar:
```javascript
const tasksValidator = require('../validators/tasks');

router.post('/create', async (req, res) => {
  const validation = await tasksValidator.createValidator(req.body);
  if (!validation.status) return res.status(400).json({ status: false, error: validation.error });

  const task = await tasksController.create(validation.data);
  res.json({ status: true, data: task });
});
```
Sin try/catch alrededor de la llamada al controlador — mismo tradeoff ya
documentado en `smapp_backend`/`PROJECT-CONVENTIONS.md` (el validador ya
atrapó los casos esperados; un fallo real de DB aquí es un caso no
esperado que no se enmascara).

**`src/controllers/tasks.js`** — agregar:
```javascript
async function create(data) {
  return models.Task.create({
    title: data.title,
    done: data.done
  });
}
```
Campo por campo, nunca `models.Task.create(data)` crudo — cubre R4
directamente.

## Forma exacta de las validaciones y su error

| Caso                                   | HTTP | Body de respuesta                              |
|-----------------------------------------|------|--------------------------------------------------|
| `title` válido (1-200 chars)             | 200  | `{status: true, data: {id, title, done}}`         |
| `title` ausente                          | 400  | `{status: false, error: "\"title\" is required"}` (mensaje real generado por Joi) |
| `title` vacío (`""`)                     | 400  | `{status: false, error: "\"title\" is not allowed to be empty"}` |
| `title` > 200 caracteres                 | 400  | `{status: false, error: "\"title\" length must be less than or equal to 200 characters long"}` |
| `title` no-string (número, null, etc.)   | 400  | `{status: false, error: "\"title\" must be a string"}` |
| `done` ausente                           | 200  | persiste `done: false` en la fila creada          |

Los mensajes de error exactos son los que Joi genera por defecto para
esas reglas — no se sobreescriben con `.messages()` porque no hay
precedente en este substrate que lo requiera (mantiene el validador
simple, alineado con "no reinventar" del protocolo).

## Alternativas descartadas

1. **Reusar `isValidTitle` directamente en la ruta, sin Joi.** Descartado:
   el propio comentario en `src/utils/validate.js` señala que esta función
   es la base de un futuro schema Joi, no un sustituto de la capa de
   validación HTTP. Usar solo `isValidTitle` en la ruta rompería la
   convención de 3 capas (`routes/validators/controllers`) que
   `PROJECT-CONVENTIONS.md` establece para todo el proyecto, y dejaría la
   ruta con lógica de validación inline en vez de en `src/validators/`.
   Se mantiene `isValidTitle` intacto para su propio unit test — el Joi
   schema es una capa adicional, no un reemplazo.
2. **Crear `src/routes/tasks-create.js` como archivo separado.** Descartado:
   el precedente (`GET /api/tasks`) y la convención general del proyecto
   usan un solo archivo de router por recurso (`tasks.js`); partir por
   verbo HTTP no tiene precedente en este substrate y fragmentaría
   innecesariamente un recurso con solo 2 endpoints.
3. **Responder 201 en vez de 200 en creación exitosa.** Descartado: el
   `acceptance` de la feature dice literalmente "responde
   {status:true, data:{...}}" sin especificar código HTTP distinto de
   200, y el único precedente de respuesta exitosa en este substrate
   (`GET /api/tasks`, `GET /health`) usa 200 en todos los casos vía
   `res.json(...)` sin `res.status(...)` explícito. Introducir 201 sin
   precedente ni pedido explícito sería inventar comportamiento no
   soportado por el `acceptance` — regla dura del protocolo del
   spec_author.

## Gaps conocidos (fuera de alcance de este spec)

- `openapi.yaml` no se actualiza con `POST /api/tasks/create` — el
  `acceptance` de la feature no lo pide y el contrato OpenAPI está
  documentado en `PROJECT-CONVENTIONS.md` como "escrito, no verificado
  corriendo" (no está aún wireado en `app.js`). Añadirlo queda para una
  sesión de LEARN separada si el humano lo pide.
