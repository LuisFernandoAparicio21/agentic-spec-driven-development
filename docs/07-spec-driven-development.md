# Spec Driven Development (SDD)

> Flujo estilo Kiro: requirements → design → tasks → código. El código no
> se escribe hasta que el spec está aprobado por un humano. Referencia de
> origen: [betta-tech/harness-sdd](https://github.com/betta-tech/harness-sdd).

## Por qué esto es distinto de la etapa PLAN original

El resto de este repo (`docs/01-planning-phase.md`) describe un plan en
prosa: archivos a tocar, reglas de validación, cómo se verifica. Eso sigue
siendo suficiente para cambios pequeños o features sin `"sdd": true`. SDD
es la versión más rigurosa para features donde el costo de un requisito
ambiguo es alto: convierte el plan en 3 artefactos estructurados,
verificables y trazables, en vez de un párrafo que un reviewer humano tiene
que interpretar.

## Estructura

Cada feature con `"sdd": true` en `feature_list.json` tiene una carpeta
dedicada en cuanto deja `pending`:

```
specs/<id>-<slug>/
├── requirements.md   # QUÉ se necesita (notación EARS)
├── design.md         # CÓMO se construirá (decisiones técnicas)
└── tasks.md          # PASOS concretos a implementar
```

`<id>` es el `id` de la feature en `feature_list.json`; `<slug>` es una
versión corta y legible del `title`.

## Estados de una feature

| Estado         | Significado                                                    |
|----------------|------------------------------------------------------------------|
| `pending`      | Sin spec. El `spec_author` es el primero en actuar.               |
| `spec_ready`   | Spec redactado. Esperando aprobación humana. NO se toca código.   |
| `in_progress`  | Spec aprobado. `implementer` trabajando.                          |
| `done`         | Verificado en verde, `reviewer` aprobó, sesión cerrada.            |
| `blocked`      | Atascado. Razón en `progress/current.md` o `progress/spec_<id>.md`.|

## La puerta de aprobación humana

El flujo automático se detiene **una vez**: cuando el `spec_author`
termina sus tres archivos, marca la feature como `spec_ready` y para. El
humano lee `specs/<id>-<slug>/` y dice "aprobado" (o pide cambios).

Solo entonces el `leader` transiciona `spec_ready → in_progress` y lanza
el `implementer`.

```
pending → [spec_author] → spec_ready → ⏸ HUMANO → in_progress → [implementer → reviewer] → done
```

## requirements.md — EARS estricto

Ver `.claude/agents/spec_author.md` para la tabla completa de los 5
patrones EARS y las reglas duras (un `DEBE` por requirement, sin verbos
blandos, id estable `R<n>`).

## Trazabilidad sin suite de tests automatizada

El repo de referencia (`harness-sdd`) asume que cada `R<n>` se verifica
con un test automatizado (`tests/test_*.py`). La mayoría de proyectos API
reales que este harness gobierna (empezando por `smapp_backend`) **no
tienen suite de tests** — la verificación es manual, contra una DB real,
documentada por caso (ver el formato de Thunder Client en el `CLAUDE.md`
de ese proyecto).

## Unit vs. integration — cuál escribir en tasks.md

Para proyectos que sí adoptan una suite (ver `examples/harness-substrate`,
que usa Vitest), cada tarea de verificación en `tasks.md` DEBE decir
explícitamente cuál de los dos es, no dejarlo implícito:

- **Unit test** (`tests/unit/`) — prueba lógica pura, sin DB, sin servidor,
  sin red: validadores, funciones de formato/cálculo, getters/setters de
  modelo. Corre en milisegundos. Un `R<n>` que describe una regla de
  validación (`"X debe ser un entero ≥1"`) se cubre aquí.
- **Integration test** (`tests/integration/`) — servidor real escuchando +
  DB real, petición HTTP real (`fetch`/`supertest`), mismo principio que
  VERIFY manual (`docs/03-runtime-verification.md`) pero automatizado. Un
  `R<n>` que describe el comportamiento observable de un endpoint completo
  (`"GET /x responde {status:true,data:[...]}"`) se cubre aquí — nunca con
  un unit test que le hace mock a la capa de ruteo o al modelo, porque eso
  deja de probar lo que el request real haría.

Regla dura: un `R<n>` sobre una regla de validación aislada no necesita
integration test si ya tiene su unit test — pero un `R<n>` sobre el
comportamiento de un endpoint SIEMPRE necesita integration test, tenga o
no también un unit test de apoyo. `tasks.md` debe nombrar el archivo
exacto (`tests/unit/<nombre>.test.js` o `tests/integration/<nombre>.test.js`).

La regla de trazabilidad no cambia, solo el tipo de evidencia aceptada:

- **Con suite de tests**: cada `R<n>` → un test concreto que lo cubre.
- **Sin suite de tests**: cada `R<n>` → un Caso de Thunder Client (o
  equivalente) documentado con Método/URL/Body/Resultado esperado, y su
  evidencia real (request/response/estado de DB) capturada en
  `progress/review_<id>.md` durante VERIFY.

En ambos casos, el `reviewer` rechaza si algún `R<n>` se queda sin
evidencia — la forma de la evidencia se adapta al proyecto, la exigencia
de que exista no.

## Cuándo NO aplica SDD

Features con `"sdd": false` o sin el campo `sdd` no pasan por
`spec_author` — usan el flujo simple de `docs/01-planning-phase.md` (plan
en prosa en `progress/current.md`). Reserva SDD para features donde vale
la pena el costo de escribir 3 archivos: contratos ambiguos, endpoints con
varias reglas de validación cruzadas, o cualquier caso donde ya haya
habido un round de review por un requisito mal entendido.
