# CHECKPOINTS — Evaluación del estado final

> En sistemas multi-agente no se evalúa el camino, se evalúa el destino.
> Estos son los checkpoints objetivos que un juez (humano o IA) puede usar
> para decidir si el harness está sano. Estructura C1-C5 calcada de
> [betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes),
> adaptada a Express + Sequelize sobre `examples/harness-substrate/`.

## C1 — El arnés está completo

- [ ] Existen los 4 archivos base: `AGENTS.md`, `init.sh`, `feature_list.json`,
      `progress/current.md`.
- [ ] Existe `examples/harness-substrate/PROJECT-CONVENTIONS.md`.
- [ ] `./init.sh` termina con exit code 0.

## C2 — El estado es coherente

- [ ] Como mucho una feature en `in_progress` en `feature_list.json`.
- [ ] Toda feature `done` tiene un `progress/review_<id>.md` con veredicto
      `APPROVED` y evidencia de VERIFY pegada.
- [ ] `progress/current.md` está vacío (plantilla) o describe la sesión
      activa — no contiene basura de sesiones anteriores.

## C3 — El código respeta la arquitectura

- [ ] `examples/harness-substrate/src/` sigue la capa routes → validators →
      controllers descrita en `PROJECT-CONVENTIONS.md` — sin acceso directo
      a la DB desde una ruta.
- [ ] Ningún controlador reenvía un objeto `req.body`/`data` crudo a
      `.create()`/`.update()` — construcción explícita campo por campo.
- [ ] No hay `console.log` sueltos de debug ni TODOs sin contexto.

## C4 — La verificación es real

- [ ] Cada feature `done` tiene al menos una petición HTTP real (golden
      path) y una con input inválido, con respuesta completa pegada en su
      `progress/review_<id>.md`.
- [ ] Toda escritura de prueba en `substrate.sqlite` fue inspeccionada
      directamente (no inferida de la respuesta HTTP) y limpiada en la
      misma pasada.
- [ ] `bash examples/harness-substrate/init.sh`-equivalente (el bloque VERIFY
      dentro de `./init.sh` raíz) corre en verde.

## C5 — La sesión se cerró bien

- [ ] No hay archivos sin trackear sospechosos (`node_modules/`,
      `*.sqlite` fuera de `.gitignore`).
- [ ] `progress/history.md` tiene una entrada por la última sesión.
- [ ] La última feature trabajada está reflejada en su estado correcto en
      `feature_list.json`.
- [ ] Si algo debía volverse regla durable, está en
      `examples/harness-substrate/PROJECT-CONVENTIONS.md` — el silencio en
      esta pregunta reprueba el checkpoint aunque todo lo demás pase.
- [ ] No hay branches publicadas de ciclos abandonados/rehechos sin
      reportar al humano — una branch vacía o a medias de un spec que se
      descartó no debería quedar sin mención solo porque la feature nunca
      llegó a `done`.

---

**Cómo usar este archivo:** el subagente `reviewer`
(`.claude/agents/reviewer.md`) recorre cada checkbox, marca `[x]` o `[ ]`,
y rechaza el cierre de sesión si quedan boxes vacíos en C1-C5.
