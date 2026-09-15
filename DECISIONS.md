# DECISIONS — ADR log
| ID | Fecha | Decisión | Contexto |
|----|-------|----------|----------|
| ADR-001 | 2026-09-14 | FastAPI + SQLite + HTML/JS | Stack aprobado para F01. MVP: CRUD inventario. |
| ADR-002 | 2026-09-14 | validate.sh como puerta única + SQLModel como ORM | F01: puerta lint+typecheck+tests+boot. SQLModel unifica modelo SQLAlchemy y schemas Pydantic sin Alembic (tablas vía create_all en init_db). |
| ADR-003 | 2026-09-14 | Frontend HTML/JS vanilla servido por FastAPI StaticFiles | F02: sin SPA ni build tools. FastAPI monta /static y sirve index.html en /; app.js (fetch vanilla) consume /api/products. Sin deps nuevas. |