#!/usr/bin/env bash
set -euo pipefail
echo "== validate.sh =="
if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  echo "[lint/typecheck/tests] — se ejecutará según stack de F01"
fi
# placeholder: el agente F01 debe implementar checks reales
echo "validate.sh: sin implementación aún (F01 lo completará)"
exit 0
