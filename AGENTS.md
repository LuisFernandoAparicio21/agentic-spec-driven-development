# AGENTS.md — Mapa de navegación para agentes de IA

> Este archivo es el **punto de entrada** para cualquier agente que trabaje en
> este repositorio. NO es una biblia de reglas: es un **mapa**. Lee solo lo
> que necesites cuando lo necesites (divulgación progresiva). Estructura
> calcada de
> [betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes),
> adaptada a Express + Sequelize.

---

## 1. Antes de empezar (obligatorio)

1. Ejecuta `./init.sh` y verifica que termina sin errores. Si falla, **para**
   y resuelve el entorno antes de tocar código.
2. Lee `progress/current.md` para entender en qué estado quedó la última sesión.
3. Lee `feature_list.json` y elige **una** tarea con estado `pending`. No
   trabajes en más de una a la vez.

## 2. Mapa del repositorio

| Archivo / carpeta                                     | Qué contiene                                               | Cuándo leerlo |
|---------------------------------------------------------|--------------------------------------------------------------|----------------|
| `feature_list.json`                                    | Lista de tareas con estado (pending/spec_ready/in_progress/done/blocked) | Siempre, al empezar |
| `specs/<id>-<slug>/`                                     | requirements/design/tasks (Kiro-style) para features `"sdd":true` | Antes de implementar/revisar una feature sdd:true |
| `progress/current.md`                                   | Estado de la sesión actual                                   | Siempre, al empezar |
| `progress/history.md`                                   | Bitácora append-only de sesiones anteriores                  | Si necesitas contexto histórico |
| `METHODOLOGY.md`                                        | El loop SPEC→LEARN completo y por qué existe                 | Antes de tu primera sesión en este repo |
| `docs/01-07...md`                                        | Un deep-dive por fase del loop (07 = Spec Driven Development) | Cuando estés en esa fase |
| `examples/harness-substrate/PROJECT-CONVENTIONS.md`      | Stack, capas (routes/validators/controllers), convenciones del revisor acumuladas | Antes de implementar o revisar cualquier código |
| `CHECKPOINTS.md`                                         | Criterios objetivos de "estado final correcto" (C1-C5)        | Para auto-evaluarte, y siempre antes de cerrar sesión |
| `.claude/agents/`                                         | Definiciones de subagentes (leader, implementer, reviewer)    | Si orquestas trabajo |
| `.claude/settings.json`                                   | Hooks que fuerzan `./init.sh` al cerrar sesión                | No necesitas leerlo, pero no puedes saltarlo |
| `examples/harness-substrate/src/`                          | Código de la app (el substrate real que el harness opera)     | Para implementar |

## 3. Reglas duras (no negociables)

- **Una sola feature a la vez.** No mezcles cambios de varias tareas en la
  misma sesión — ver `feature_list.json`'s `rules.one_feature_at_a_time`.
- **No declares una tarea `done` sin verificación real en verde.** Ejecuta
  `./init.sh` y confirma con evidencia pegada (request/response/DB), no con
  una afirmación.
- **Documenta lo que haces** en `progress/current.md` mientras trabajas, no
  al final.
- **Deja el repositorio limpio** antes de cerrar la sesión (ver §5).
- **Si no sabes algo, busca en `docs/` o `PROJECT-CONVENTIONS.md`** antes de
  inventarlo.

## 4. Cómo elegir una tarea

```
1. Abre feature_list.json
2. Filtra por status == "pending"
3. Coge la de menor "id"
4. Cambia su status a "in_progress" y guarda
5. Anota en progress/current.md: feature, hora de inicio, plan breve
   (esto solo ocurre DESPUÉS de que el humano aprobó el plan — ver
   METHODOLOGY.md sección PLAN)
```

## 5. Cierre de sesión (lifecycle)

Antes de terminar:

1. Ejecuta `./init.sh` — todo verde.
2. Si la tarea está acabada y aprobada por el reviewer Y el humano dio el
   HUMAN GATE: marca `status: "done"` en `feature_list.json`.
3. Mueve el resumen de `progress/current.md` al final de `progress/history.md`.
4. Vacía `progress/current.md` dejando solo la plantilla.
5. No dejes archivos temporales, ni filas de prueba sin borrar en
   `substrate.sqlite`, ni TODOs sin contexto.
6. Pregunta explícitamente: ¿algo de esta sesión debe volverse una regla
   durable? Si sí, añádelo a
   `examples/harness-substrate/PROJECT-CONVENTIONS.md` — ver
   `docs/06-review-feedback-to-durable-convention.md`.

## 6. Si te bloqueas

- Relee la sección relevante de `docs/` o `PROJECT-CONVENTIONS.md`.
- Si la herramienta no hace lo que esperas, **no inventes un workaround**:
  documenta el bloqueo en `progress/current.md` con `status: "blocked"` y
  para la sesión.
