#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/ruff" ]]; then
  BIN="$ROOT/.venv/bin"
  echo "== validate.sh (usando .venv) =="
else
  BIN=""
  echo "== validate.sh (binarios del PATH) =="
fi

run() {
  local tool="$1"
  shift
  if [[ -n "$BIN" ]]; then
    "$BIN/$tool" "$@"
  else
    "$tool" "$@"
  fi
}

echo ""
echo "[1/4] ruff check ."
run ruff check .

echo ""
echo "[2/4] mypy app"
run mypy app

echo ""
echo "[3/4] pytest app/tests"
run pytest app/tests

echo ""
echo "[4/4] boot check: import app + TestClient /health"
run python - <<'PY'
from fastapi.testclient import TestClient

from app.main import app

with TestClient(app) as client:
    resp = client.get("/health")
    assert resp.status_code == 200, f"status={resp.status_code}"
    assert resp.json() == {"status": "ok"}, resp.json()
print("boot OK: /health -> 200")
PY

echo ""
echo "== validate.sh: ALL CHECKS PASSED =="