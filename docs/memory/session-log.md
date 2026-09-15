# Session Log

## 2026-09-14 — F01: Inventario CRUD (productos) ✅
- **Decisión stack**: FastAPI + SQLite + SQLModel + HTML/JS (ADR-001, ADR-002). MVP: CRUD de productos (nombre, categoría, volumen, precio en centavos, stock).
- **Estructura**: `app/` (config, database, models/product, api/routes/products), tests aislados en `app/tests/`, `validate.sh` como puerta única.
- **Build T1-T5**: T1 esqueleto, T2 modelo+db, T3 endpoints CRUD+filtros, T4 tests (15 passed), T5 validate.sh+README (todo verde).
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 15 passed ✅ boot /health 200 ✅. Push a GitHub OK.
- **Notas**: precio en centavos (int) para evitar floats; SQLite sin Alembic (create_all); warning de deprecación httpx/starlette en tests (no bloqueante).

## 2026-09-14 — F02: Frontend HTML/JS ✅
- **Decisión stack**: ADR-003. Frontend vanilla servido por FastAPI (`StaticFiles` en `/static` + `index.html` en `/`). Sin SPA ni build tools, sin deps nuevas.
- **Estructura**: `app/static/` (index.html, style.css, app.js), `app/main.py` (mount estáticos + root), `app/tests/test_frontend.py` (E2E vía TestClient).
- **Build T1-T5**: T1 static files + index skeleton, T2 listar + filtros, T3 crear/editar, T4 borrar + UX polish, T5 E2E tests + validate.sh.
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 23 passed ✅ boot /health 200 ✅. `node --check app.js` OK. Push a GitHub OK.
- **Notas**: fix de test T1 (content-type `text/css; charset=utf-8` → `startswith`); el router `auto/best-free` exige prompts mínimos (sin `@spec` completo) por límite 4K.