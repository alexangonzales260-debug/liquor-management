# F01 Tasks Breakdown

## T1 — Project skeleton
- **Goal**: Initialize the app so it can start and be tested.
- **Files**: `pyproject.toml`, `app/__init__.py`, `app/config.py`, `app/database.py`, `app/main.py` (empty FastAPI app).
- **Verify**: `python -m app.main` → no errors; expected output: app runs (uvicorn) or exits cleanly.
- **Commit**: `feat(f01): project skeleton`

## T2 — Product model & DB init
- **Goal**: Define `Product` table and initialize SQLite schema.
- **Files**: `app/models/product.py`, `app/database.py` (update `init_db`), `app/main.py` (call init on startup).
- **Verify**: `python -c "from app.database import init_db; init_db()"` then `sqlite3 inventory.db ".schema products"` → table `products` with columns id, name, category, volume_ml, price_cents, stock, created_at, updated_at.
- **Commit**: `feat(f01): product model & db init`

## T3 — Product CRUD endpoints
- **Goal**: Expose `GET/POST/PUT/DELETE` for products with filtering and validation.
- **Files**: `app/api/routes/products.py`, `app/main.py` (include router).
- **Verify**: `pytest` with a quick smoke call; alternatively `curl -X POST localhost:8000/api/products` returns 422 on empty body and 201 with a valid body; `curl localhost:8000/api/products` returns a list.
- **Commit**: `feat(f01): product CRUD endpoints`

## T4 — Tests
- **Goal**: Verify CRUD behavior with an isolated test DB.
- **Files**: `app/tests/conftest.py`, `app/tests/test_products.py`.
- **Verify**: `pytest app/tests -v` → all tests pass (e.g., `5 passed`), covering: list, create, detail, replace, delete, category + search filters, validation errors (400/404).
- **Commit**: `feat(f01): product CRUD tests`

## T5 — Validate script & docs
- **Goal**: Provide a real `validate.sh` and project README.
- **Files**: `validate.sh`, `README.md` (install/run/test instructions).
- **Verify**: `./validate.sh` → passes: `ruff check .` clean, `mypy app` type clean, `pytest` all tests pass.
- **Commit**: `feat(f01): validate script & docs`