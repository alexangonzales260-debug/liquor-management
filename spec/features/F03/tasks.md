# F03 Tasks Breakdown

## T1 — Sales model & config
- **Goal**: New `sales` table via `create_all` (no Alembic) and `STOCK_LOW_THRESHOLD` setting.
- **Files**: `app/models/sale.py` (SQLModel `Sale`: `id` PK, `product_id` FK→`products.id`, `qty` `gt=0`, `unit_price_cents`, `total_cents`, `created_at` default utcnow), `app/database.py` (import `Sale` so metadata includes it), `app/config.py` (add `STOCK_LOW_THRESHOLD: int = 5`).
- **Verify**: `python -c "from app.database import init_db; init_db()"` then `sqlite3 inventory.db ".schema sales"` → table `sales` with `id`, `product_id REFERENCES products(id)`, `qty`, `unit_price_cents`, `total_cents`, `created_at`. Existing products schema unchanged.
- **Commit**: `feat(f03): sales model & config`

## T2 — Register sale endpoint
- **Goal**: `POST /api/sales` creates a sale and decrements stock atomically: 404 unknown product, 400 `qty > stock`, 422 `qty <= 0`, 201 ok. `unit_price_cents` snapshots `products.price_cents`; `total_cents = qty * unit_price_cents`.
- **Files**: `app/api/routes/sales.py` (new: `POST /api/sales`, `SalesInput {product_id, qty: int gt=0}`), `app/database.py` (move shared `get_db` here), `app/api/routes/products.py` (import `get_db` from `app.database`), `app/main.py` (include sales router), `app/tests/conftest.py` (override `get_db` from `app.database`).
- **Verify**: `.venv/bin/pytest app/tests -v` → new `test_sales.py` cases pass: sale 201 + stock decremented (GET product shows `stock - qty`), 404 unknown id, 400 over-stock, 422 qty 0/negative.
- **Commit**: `feat(f03): register sale endpoint`

## T3 — Sales list & dashboard stats
- **Goal**: `GET /api/sales` returns sales newest-first; `GET /api/stats/dashboard` returns `{total_products, total_sales, total_revenue_cents, low_stock:[{id,name,stock}]}` with `low_stock` = `stock <= STOCK_LOW_THRESHOLD` ordered by stock asc.
- **Files**: `app/api/routes/sales.py` (`GET ""`), `app/api/routes/stats.py` (new), `app/main.py` (include stats router), `app/tests/test_sales.py` (dashboard shape + low-stock threshold).
- **Verify**: `.venv/bin/pytest app/tests -v` → dashboard tests pass: totals correct after seeded sales, low-stock includes e.g. stock 5 and 3 rows, excludes stock 10.
- **Commit**: `feat(f03): sales list & dashboard stats`

## T4 — Multi-page layout & dashboard
- **Goal**: Frontend becomes hash-routed: header + sidebar with links `#/dashboard`, `#/products`, `#/sales`; three view containers; hash router in `app.js` shows one at a time; default route → `#/dashboard`; dashboard view renders `GET /api/stats/dashboard` (cards + low-stock table).
- **Files**: `app/static/index.html` (rewrite: layout + views), `app/static/style.css` (sidebar/flex layout), `app/static/app.js` (hash router + dashboard fetch/render).
- **Verify**: `.venv/bin/pytest app/tests -v` → layout assertions pass on `/` HTML (`header`, sidebar, `a[href="#/dashboard"]`, `#view-dashboard`, `#view-products`, `#view-sales`). Manual: `/` shows dashboard; clicking sidebar switches views without reload.
- **Commit**: `feat(f03): multi-page layout & dashboard`

## T5 — Sales & products views
- **Goal**: Sales view: product `<select>` + qty form → `POST /api/sales` (errors via API `detail`), and a sales table (id, product name, qty, unit price, total, date). Products view: full F02 CRUD (create/edit/delete/filters) migrated into the new layout, unchanged behavior.
- **Files**: `app/static/app.js`, `app/static/index.html`, `app/static/style.css`.
- **Verify**: `.venv/bin/pytest app/tests -v` → prior F02 CRUD/list/filter tests still green under new layout; manual: register a sale → stock drops in products view and row appears in sales table.
- **Commit**: `feat(f03): sales & products views`

## T6 — E2E tests & validate
- **Goal**: Lock F03 end-to-end: hash routing single-active-view, sales API round-trip through the page, dashboard reflects data. `validate.sh` is the only gate (CONSTRAINTS.md).
- **Files**: `app/tests/test_frontend.py` (touch: layout/routing + sales+dashboard flows), `app/tests/test_sales.py` (any remaining coverage).
- **Verify**: `cd /home/leonardo/Escritorio/liquor-management && ./validate.sh` → `[1/4] ruff check .` clean, `[2/4] mypy app` clean, `[3/4] pytest app/tests` all pass (F01+F02+F03), `[4/4] boot check` `/health` 200, ends with `== validate.sh: ALL CHECKS PASSED ==`.
- **Commit**: `feat(f03): sales e2e tests & validate`