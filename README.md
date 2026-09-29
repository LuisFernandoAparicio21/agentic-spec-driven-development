<div align="center">

# Agentic Spec-Driven Development for API Engineering

**Una metodología probada en producción para construir APIs REST con un agente de IA como colaborador real — no autocompletado, no "vibe-coding".**

<br>

![Methodology](https://img.shields.io/badge/method-spec--driven-2563EB?style=for-the-badge)
![Node](https://img.shields.io/badge/Node.js-Express%204-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Sequelize](https://img.shields.io/badge/ORM-Sequelize-52B0E7?style=for-the-badge&logo=sequelize&logoColor=white)
![Claude Code](https://img.shields.io/badge/agent-Claude%20Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-16A34A?style=for-the-badge)

<sub>Cada endpoint atraviesa el mismo bucle, siempre, sin atajos.</sub>

</div>

---

## Contenido

- [El bucle](#el-bucle)
- [El harness](#el-harness)
- [Por qué existe](#por-qué-existe)
- [Stack validado](#stack-validado)
- [Por dónde empezar](#por-dónde-empezar)
- [El harness es parte del repo](#el-harness-es-parte-del-repo)
- [Relación con otras herramientas](#relación-con-otras-herramientas)
- [Licencia](#licencia)

---

## El bucle

No es una metodología genérica de software. Está **especializada** para la forma real del trabajo de backend: entra una petición como *ruta*, un *validador* decide si está bien formada, un *controlador* habla con la base de datos, y sale una *respuesta*. Esa especificidad es lo que la hace rápida de aplicar y fácil de verificar.

```
  SPEC ──▶ PLAN ──▶ CODE ──▶ VERIFY ──▶ REVIEW ──▶ SIMPLIFY ──▶ HUMAN GATE ──▶ LEARN
   │                                                                             │
   └───────────────── la regla aprendida alimenta el SPEC del siguiente ◀────────┘
```

---

## El harness

El agente no "recuerda" en el chat: el estado vive en disco. Una sesión nueva retoma leyendo archivos, no que se lo vuelvan a contar.

```
  pending ─▶ spec_ready ─▶ ⏸ HUMAN GATE ─▶ in_progress ─▶ done
              (spec_author)                (implementer → reviewer)
                                                  │
                                      ✗ rechazado ─┘  vuelve a in_progress
```

| Rol | Responsabilidad |
|-----|-----------------|
| **leader** | Descompone y coordina. Nunca escribe código. Nunca marca `done`. |
| **spec_author** | Redacta `requirements` / `design` / `tasks` en notación EARS. No implementa. |
| **implementer** | Una feature contra un plan aprobado. Se autoverifica con `init.sh`. |
| **reviewer** | VERIFY real (HTTP + base de datos) + revisión multi-lente. Aprueba o rechaza. |

---

## Por qué existe

- [GitHub Spec Kit](https://github.com/github/spec-kit) (128k ★) demostró que escribir el plan como artefacto revisable **antes** de que exista el código funciona a escala general.
- Este repo toma esa idea y la **acota a un dominio**: el desarrollo de endpoints de API — donde el *spec* es un contrato request/response, la *verificación* es una llamada HTTP real contra una base de datos real, y la *revisión* es un conjunto de agentes especializados mirando el diff desde distintos ángulos antes de que un humano tenga que hacerlo.
- Nació y se usó **en producción**, a lo largo de decenas de pull requests fusionados sobre un backend Express + Sequelize real.
- **Nada de código fuente, lógica de negocio ni datos propietarios** de ese proyecto aparece aquí. Todo es genérico e ilustrativo.

---

## Stack validado

La **metodología** (el bucle, los principios, las etapas de review / verify / learn) es agnóstica al stack por diseño. Los **templates y ejemplos** reflejan el único stack contra el que se probó de verdad — y son honestos al respecto.

| Capa | Tecnología |
|------|------------|
| Runtime / framework | Node.js + Express 4 |
| Validación | Joi |
| ORM / base de datos | Sequelize (SQL Server vía `tedious`; aplica a cualquier BD soportada) |
| Arquitectura | Tres capas `routes → validators → controllers` |

> **Adaptarlo a otro stack** (FastAPI + Pydantic, Go, otro ORM) significa reescribir `PROJECT-CONVENTIONS.md.template` y el código de ejemplo. Las etapas, las lentes de revisión y la disciplina de verificación en `METHODOLOGY.md` y `docs/` se mantienen igual: ninguna está escrita en términos de Express, Joi o Sequelize.

---

## Por dónde empezar

| Recurso | Qué encontrarás |
|---------|-----------------|
| [`METHODOLOGY.md`](METHODOLOGY.md) | La metodología completa: por qué funciona, el flujo en la práctica, principios y guardarraíles no negociables. |
| [`AGENTS.md`](AGENTS.md) | El punto de entrada para un agente que opera *dentro* del repo: quién hace qué, dónde vive el estado y las reglas. |
| [`docs/`](docs) | Un deep-dive por fase, incluido [el ciclo de convención durable](docs/06-review-feedback-to-durable-convention.md): "el PR vuelve → arréglalo → decide si es regla". |
| [`templates/`](templates) | Convenciones de proyecto, un template de PR que convierte "¿capturar esto como regla?" en un checklist literal, y ejemplos de memoria. |
| [`examples/illustrative-review-cycle/`](examples/illustrative-review-cycle) | Un ejemplo completo en prosa: spec falso → plan → hallazgos → verificación → una ronda que rechaza el diff → qué se captura como regla. |
| [`examples/harness-substrate/`](examples/harness-substrate) | Una app Express + Sequelize (sqlite) **real y ejecutable** sobre la que el harness opera de verdad. |
| [`case-study/session-metrics.md`](case-study/session-metrics.md) | Métricas anonimizadas de uso real. |

---

## El harness es parte del repo

Tres cosas lo distinguen de "pegar `METHODOLOGY.md` en un chat y esperar que el agente lo siga":

1. **El repo es el sistema.** `CLAUDE.md` auto-carga el rol `leader` en cada sesión; `.claude/agents/`, `feature_list.json` y `progress/` son archivos versionados, no estado de conversación — una sesión nueva retoma leyendo disco.
2. **La orquestación es real, no simulada.** `leader` planifica y delega (nunca edita código); `implementer` escribe contra un plan aprobado; `reviewer` corre peticiones reales y lentes de revisión independientes.
3. **El harness se verifica a sí mismo y lo impone vía hooks.** El hook `Stop` de `.claude/settings.json` corre `init.sh` antes de que una sesión pueda cerrar — lo ejecuta el harness, no el agente, así que no se puede saltar con un reporte convincente. `CHECKPOINTS.md` le da a cada etapa una barra objetiva de aprobado / rechazado.

> Los mecanismos (nombres de archivos, el split de roles, el formato de checkpoints C1-C5, la aplicación vía hooks) están calcados de [betta-tech/ejemplo-harness-subagentes](https://github.com/betta-tech/ejemplo-harness-subagentes), adaptados de su substrate Python/CLI al Express + Sequelize de aquí.

---

## Relación con otras herramientas

Corre sobre cualquier agente de IA que soporte skills tipo slash-command (Claude Code y similares). No reemplaza a [Spec Kit](https://github.com/github/spec-kit): es una aplicación más acotada y específica de API de la misma idea de fondo, más una capa de verificación y revisión multi-agente que Spec Kit no prescribe.

---

## Licencia

**MIT** — ver [`LICENSE`](LICENSE).

<div align="center"><sub>Construido con la disciplina que documenta.</sub></div>
