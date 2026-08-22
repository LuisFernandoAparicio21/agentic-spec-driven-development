#!/usr/bin/env bash
# init.sh — verificación de entorno y del harness antes/después de cada sesión.
# El harness lo ejecuta mediante el hook Stop en .claude/settings.json, no el
# agente por su cuenta — así no se puede saltar. Adaptado de
# betta-tech/ejemplo-harness-subagentes (Python) a Node/Express/Sequelize.
set -u
cd "$(dirname "$0")"

FAIL=0
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC}   $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAIL=1; }

echo "== C1: node disponible =="
if command -v node >/dev/null 2>&1; then
  ok "node $(node --version)"
else
  fail "node no está instalado — no se puede continuar"
  exit 1
fi

echo "== C1: archivos base del arnés =="
for f in AGENTS.md feature_list.json CHECKPOINTS.md progress/current.md \
         examples/harness-substrate/PROJECT-CONVENTIONS.md; do
  if [ -f "$f" ]; then ok "$f"; else fail "falta $f"; fi
done

echo "== C2: esquema y coherencia de feature_list.json =="
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('feature_list.json', 'utf8'));
const validStatus = (data.rules && data.rules.valid_status) || ['pending','in_progress','done','blocked'];
let bad = false;
const inProgress = data.features.filter(f => f.status === 'in_progress');
if (inProgress.length > 1) {
  console.error('más de una feature in_progress: ' + inProgress.map(f => f.id).join(', '));
  bad = true;
}
for (const f of data.features) {
  if (!validStatus.includes(f.status)) {
    console.error('status inválido en ' + f.id + ': ' + f.status);
    bad = true;
  }
  if (!Array.isArray(f.acceptance) || f.acceptance.length === 0) {
    console.error('feature ' + f.id + ' sin criterios de acceptance');
    bad = true;
  }
}
process.exit(bad ? 1 : 0);
" && ok "feature_list.json coherente" || fail "feature_list.json inconsistente (ver arriba)"

echo "== C4: tests automatizados del substrate (npm test) =="
if [ ! -d examples/harness-substrate/node_modules ]; then
  warn "node_modules no existe — se salta npm test junto con el resto de VERIFY."
else
  if (cd examples/harness-substrate && npm test) > /tmp/harness_substrate_tests.log 2>&1; then
    ok "npm test en verde (unit + integration, ver /tmp/harness_substrate_tests.log)"
  else
    fail "npm test falló — ver /tmp/harness_substrate_tests.log"
    tail -20 /tmp/harness_substrate_tests.log
  fi
fi

echo "== C4: VERIFY real contra el substrate =="
if [ ! -d examples/harness-substrate/node_modules ]; then
  warn "examples/harness-substrate/node_modules no existe — corre 'npm install' ahí antes de VERIFY real. Saltando el arranque del servidor."
else
  PORT="${PORT:-3100}"
  (cd examples/harness-substrate && npm start) >/tmp/harness_substrate.log 2>&1 &
  SERVER_PID=$!
  trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

  UP=0
  for _ in $(seq 1 30); do
    if curl -s -o /dev/null "http://localhost:${PORT}/health"; then UP=1; break; fi
    sleep 0.5
  done

  if [ "$UP" -eq 1 ]; then
    RESPONSE=$(curl -s "http://localhost:${PORT}/health")
    if echo "$RESPONSE" | grep -q '"status":true'; then
      ok "GET /health -> ${RESPONSE}"
    else
      fail "GET /health respondió algo inesperado: ${RESPONSE}"
    fi
  else
    fail "el servidor del substrate no levantó a tiempo — ver /tmp/harness_substrate.log"
    cat /tmp/harness_substrate.log
  fi

  kill "$SERVER_PID" 2>/dev/null || true
  trap - EXIT
fi

echo "=========================="
if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}init.sh: TODO OK${NC}"
else
  echo -e "${RED}init.sh: HAY FALLOS — no declares ninguna feature 'done' hasta resolverlos${NC}"
fi
exit "$FAIL"
