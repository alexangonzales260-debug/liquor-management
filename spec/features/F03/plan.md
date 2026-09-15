# F03 Plan

## Tech Stack
- **FastAPI + SQLModel + SQLite** — existing stack; schema evolves via `create_all` in `init_db` (no Alembic, ADR-002).
- **Vanilla HTML/CSS/JS** — hash-routed multi-page frontend served by existing `StaticFiles`; no framework, no build step.
- **No new dependencies** — constraíto por CONSTRAINTS.md (sin deps nuevas sin aprobación).

## Key design decisions
- `get_db` se extrae a `app/database.py` (hoy vive en `api/routes/products.py`) para que `conftest.py` sobrescriba una sola dependencia compartida por products/sales/stats routers.
- `unit_price_cents` es snapshot del precio del producto al momento de la venta; `total_cents` se calcula en servidor (el cliente solo envía `product_id` + `qty`).
- Descuento de stock e inserción de la venta en la misma transacción.

## Directory Structure (to create / touch)
```
app/
├── config.py                       # (touch) + STOCK_LOW_THRESHOLD = 5
├── database.py                     # (touch) + get_db compartido; import Sale en init_db
├── models/
│   └── sale.py                     # (create) SQLModel Sale (tabla sales)
├── api/routes/
│   ├── products.py                 # (touch) usar get_db importado de database
│   ├── sales.py                    # (create) POST/GET /api/sales
│   └── stats.py                    # (create) GET /api/stats/dashboard
├── main.py                         # (touch) include_router(sales, stats)
├── static/
│   ├── index.html                  # (rewrite) header + sidebar + 3 views
│   ├── style.css                   # (touch) layout sidebar/multi-view
│   └── app.js                      # (rewrite) hash router + views
└── tests/
    ├── conftest.py                 # (touch) override get_db desde database
    ├── test_sales.py               # (create) sales API + dashboard tests
    └── test_frontend.py            # (touch) E2E hash-routing + ventas/dashboard
validate.sh                          # exit gate, must stay green
```

## Atomic Tasks
| Task | Description | Commit |
|------|-------------|--------|
| T1 | `Sale` model + tabla `sales` vía `create_all` + `STOCK_LOW_THRESHOLD` en config. | `feat(f03): sales model & config` |
| T2 | `POST /api/sales`: registro + descuento de stock (404/400/201) + `get_db` compartido + conftest. | `feat(f03): register sale endpoint` |
| T3 | `GET /api/sales` (nuevo→viejo) + `GET /api/stats/dashboard` (totales + low stock). | `feat(f03): sales list & dashboard stats` |
| T4 | Frontend multi-página: header + sidebar + hash router + vista dashboard. | `feat(f03): multi-page layout & dashboard` |
| T5 | Vista ventas (form + tabla) y migración de productos al nuevo layout. | `feat(f03): sales & products views` |
| T6 | E2E tests (routing, ventas, dashboard) + `validate.sh` verde como puerta. | `feat(f03): sales e2e tests & validate` |

Justificación del orden: T1 define el modelo/schema (precondición); T2 provee la venta atómica; T3 agrega consultas y stats; T4 establece el layout multi-página que todo el frontend necesita; T5 rellena ventas y migra productos; T6 cierra con la puerta `validate.sh` (CONSTRAINTS.md).