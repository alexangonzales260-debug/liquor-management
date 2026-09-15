# Session Log

## 2026-09-14 — F01: Inventario CRUD (productos) ✅
- **Decisión stack**: FastAPI + SQLite + SQLModel + HTML/JS (ADR-001, ADR-002). MVP: CRUD de productos (nombre, categoría, volumen, precio en centavos, stock).
- **Estructura**: `app/` (config, database, models/product, api/routes/products), tests aislados en `app/tests/`, `validate.sh` como puerta única.
- **Build T1-T5**: T1 esqueleto, T2 modelo+db, T3 endpoints CRUD+filtros, T4 tests (15 passed), T5 validate.sh+README (todo verde).
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 15 passed ✅ boot /health 200 ✅. Push a GitHub OK.
- **Notas**: precio en centavos (int) para evitar floats; SQLite sin Alembic (create_all); warning de deprecación httpx/starlette en tests (no bloqueante).