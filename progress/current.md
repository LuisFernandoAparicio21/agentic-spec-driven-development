# Current plan

_No hay ciclo en curso. El subagente `leader` (`.claude/agents/leader.md`)
sobreescribe este archivo con el plan aprobado al inicio de cada etapa PLAN
— ver `AGENTS.md` y `METHODOLOGY.md` sección 2. Al cerrar sesión, su
contenido se mueve a `progress/history.md` y este archivo vuelve a la
plantilla — ver `AGENTS.md` sección 5._

Plantilla para el próximo plan:

```
Feature en curso: <id de feature_list.json> — <title>
Hora de inicio: <fecha/hora>

## Contrato
<method, url, params, response shape — copiado de feature_list.json>

## Archivos
- <archivo> — <por qué>

## Reusado
- <helper/patrón existente reusado, o "ninguno — primer endpoint de su tipo">

## Validación
- <regla> → <forma exacta del error>

## Plan de verificación
- <qué request(s) se mandarán, qué estado de DB se va a revisar>
```
