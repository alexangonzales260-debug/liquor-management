# F02 Tasks Breakdown

## T1 — Static files & index skeleton
- **Goal**: FastAPI serves the frontend: `/` returns `index.html`, `/static/*` serves CSS/JS. HTML/CSS skeleton (table, filter bar, form) visible with no JS logic yet.
- **Files**: `app/main.py` (mount `StaticFiles` at `/static`, root route via `FileResponse`), `app/static/index.html`, `app/static/style.css`, `app/static/app.js` (minimal stub), `app/tests/test_frontend.py`, `app/tests/conftest.py` (if needed for TestClient + static).
- **Verify**:
  - `cd /home/leonardo/Escritorio/liquor-management && .venv/bin/pytest app/tests -v` → includes `test_frontend.py` passing: `/` returns `200` with `text/html`, `/static/style.css` returns `200` with `text/css`, `/static/app.js` returns `200`.
  - Optional manual: `uvicorn app.main:app` then `curl -s localhost:8000/ | head -5` shows `<!DOCTYPE html>`.
- **Commit**: `feat(f02): static files & index skeleton`

## T2 — List products & filters
- **Goal**: `app.js` fetches `GET /api/products` (with optional `category` and `search` query params), renders the table (name, category, volume, formatted price, stock), and toggles loading / error ("request failed") / empty ("no products") states. Filter inputs trigger a re-fetch on change.
- **Files**: `app/static/app.js`, `app/static/index.html` (wire IDs/events), `app/static/style.css` (status classes).
- **Verify**: `./validate.sh` → `ALL CHECKS PASSED` (Boot: `/health` 200). Manual: seed 2-3 products via POST, open `/`, table shows them; set a `search` filter and verify only matching rows remain (table re-renders from API).
- **Commit**: `feat(f02): list products & filters`

## T3 — Create & edit products
- **Goal**: Form validates (`name` non-empty; `volume_ml`, `price_cents`, `stock` non-negative integers) and submits `POST /api/products`; Edit pre-fills the form from a row and switches to `PUT /api/products/{id}`. After save the list is re-fetched. 4xx responses show the API `detail` in the status area.
- **Files**: `app/static/app.js`, `app/static/index.html` (form + Edit buttons), `app/static/style.css`.
- **Verify**: `./validate.sh` → green. Manual: submit empty name → validation message, no request; valid POST → row appears; click Edit → form pre-filled, save → row updated.
- **Commit**: `feat(f02): create & edit products`

## T4 — Delete & UX polish
- **Goal**: Delete button asks `confirm()` then `DELETE /api/products/{id}` and re-fetches the list; final CSS polish (form layout, table striping, buttons) and currency formatting util (`cents → $12.99`).
- **Files**: `app/static/app.js`, `app/static/style.css`.
- **Verify**: `./validate.sh` → green. Manual: delete a row → confirm accept → row gone; confirm cancel → row remains.
- **Commit**: `feat(f02): delete & ux polish`

## T5 — Frontend E2E tests
- **Goal**: Lock the whole flow in `app/tests/test_frontend.py` with `TestClient` (works with `StaticFiles`): root HTML contains table/form/filter elements; assets serve correctly; and a full create→list→edit→delete round-trip through the API as exercised by the page. `validate.sh` is the exit gate.
- **Files**: `app/tests/test_frontend.py`.
- **Verify**: `cd /home/leonardo/Escritorio/liquor-management && ./validate.sh` → outputs `[1/4] ruff check .` clean, `[2/4] mypy app` clean, `[3/4] pytest app/tests` all pass (existing F01 tests + new frontend tests), `[4/4] boot check` OK, ends with `== validate.sh: ALL CHECKS PASSED ==`.
- **Commit**: `feat(f02): frontend e2e tests`