# F03 Specification

## Context & Goal
Add sales processing on top of the F01/F02 inventory: a `sales` table records each sale and atomically decrements product stock, a stats dashboard exposes low-stock/products/sales totals, and the frontend becomes a multi-page app (hash-routed: dashboard / products / sales) while keeping the existing products CRUD. No new Python dependencies and no Alembic (schema evolves via `create_all` in `init_db`, per ADR-002).

## Data Model (`sales` table)
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | auto-increment |
| `product_id` | integer FK → `products.id` | NOT NULL |
| `qty` | integer | `> 0` |
| `unit_price_cents` | integer | snapshot of `products.price_cents` at sale time |
| `total_cents` | integer | computed server-side: `qty * unit_price_cents` |
| `created_at` | timestamp | default now (UTC) |

- `price_cents` snapshot avoids subsequent product price edits rewriting history.
- Stock is decremented in the same transaction that creates the sale.

## Config
- `Settings.STOCK_LOW_THRESHOLD: int = 5` — a product is "low stock" when `stock <= STOCK_LOW_THRESHOLD`.

## REST API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sales` | Body `{product_id: int, qty: int>0}`. 404 if product not found; 400 if `qty > stock`; 422 if `qty <= 0`; 201 with the created sale on success |
| GET | `/api/sales` | List sales (newest first) |
| GET | `/api/stats/dashboard` | `{total_products, total_sales, total_revenue_cents, low_stock: [{id, name, stock}]}` |

- POST semantics: load product, on missing → 404; on `qty > product.stock` → 400; compute `unit_price_cents = product.price_cents`, `total_cents = qty * unit_price_cents`; insert sale; `product.stock -= qty`; commit. All mutations occur atomically in one transaction.
- `low_stock` lists every product with `stock <= STOCK_LOW_THRESHOLD` ordered by `stock` asc; `total_revenue_cents` is `SUM(total_cents)` over all sales.

## Frontend (hash-routing)
- `index.html` gains: persistent **header** (title) + **sidebar** navigation with links `#/dashboard`, `#/products`, `#/sales` and three `<section>` view containers.
- `app.js` implements a tiny hash router (`hashchange` listener): shows exactly one active view, hides the others, loads data per view.
  - **`#/products`**: existing F02 create/edit/delete/filter table, migrated into the new layout unchanged in behavior.
  - **`#/sales`**: form (product `<select>`, qty input) → `POST /api/sales`; on error shows API `detail`; below, a sales table (id, product, qty, unit price, total, date).
  - **`#/dashboard`**: `GET /api/stats/dashboard` → summary cards (products, sales, revenue) + low-stock table.
- Default route (`/` or unknown hash) redirects to `#/dashboard`.
- Errors/loading/empty states reuse the F02 status-area pattern.

## Acceptance Criteria (verifiable)
- `sales` table created by `create_all` with the columns above and FK to `products`.
- `POST /api/sales` returns 201, inserts a row with `unit_price_cents`/`total_cents` correct, and decrements `products.stock` by `qty` (verified via GET product).
- `POST /api/sales` → 404 on unknown `product_id`; 400 when `qty > stock`; 422 when `qty <= 0`.
- `GET /api/sales` returns sales newest-first.
- `GET /api/stats/dashboard` returns the documented shape; `low_stock` includes products with `stock <= 5` and respects the threshold setting.
- Frontend: `/` serves a layout with sidebar + header, hash links `#/dashboard`, `#/products`, `#/sales`, and each view container has a stable id; only one view visible at a time.
- `validate.sh` fully green (ruff + mypy + pytest + boot).

## Out of Scope
- Authentication, refunds/returns, partial stock adjustments, payment details, pagination, separate frontend server, Alembic migrations, new dependencies.