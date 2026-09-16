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

## 2026-09-15 — F03: Ventas + Dashboard multi-página ✅
- **Decisión stack & arquitectura**: ADR-004. Modelo `Sale` añadido vía `create_all` (sin Alembic). Descuento de stock atómico. Hash router en cliente vanilla (`#/dashboard`, `#/products`, `#/sales`). Umbral stock bajo en `STOCK_LOW_THRESHOLD = 5`.
- **Estructura**: `app/models/sale.py`, `app/api/routes/sales.py`, `app/api/routes/stats.py`, frontend multi-página en `app/static/` (index.html con sidebar/cards, app.js router+vistas, style.css responsive).
- **Build T1-T6**: T1 modelo Sale+config, T2 POST /api/sales+descuento, T3 GET sales+dashboard stats, T4 layout sidebar+dashboard, T5 vistas sales+products completas, T6 E2E tests (47 passed)+validate.sh.
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 47 passed ✅ boot /health 200 ✅. Push a GitHub OK con tag `F03`.

## 2026-09-15 — F04: Gestión de Categorías ✅
- **Decisión stack & arquitectura**: ADR-005. Modelo `Category` añadido vía `create_all`. Endpoints CRUD en `/api/categories` con conteo de productos, validación de unicidad de nombre y protección de borrado si hay productos asociados. Cascada de actualización de nombre hacia productos.
- **Estructura**: `app/models/category.py`, `app/api/routes/categories.py`, tests en `app/tests/test_categories.py`, vista `#/categories` en frontend y selects dinámicos en formulario/filtros de productos.
- **Build T1-T5**: T1 modelo Category+db init, T2 API CRUD categorías+tests, T3 frontend vista categorías+navegación hash, T4 integración en vista productos (selects dinámicos), T5 E2E tests+docs README+validate.sh.
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 69 passed ✅ boot /health 200 ✅. Push a GitHub OK con tag `F04`.

## 2026-09-15 — F05: Entradas / Reposición de Stock ✅
- **Decisión stack & arquitectura**: ADR-006. Modelo `Restock` añadido vía `create_all`. Endpoints en `/api/restocks` con cálculo de costo total opcional, incremento atómico de stock en transacción, historial ordenado por fecha desc. Frontend vista `#/restocks` con formulario e historial, botón "Reponer" en dashboard que navega pre-seleccionando producto.
- **Estructura**: `app/models/restock.py`, `app/api/routes/restocks.py`, tests en `app/tests/test_restocks.py`, vista `#/restocks` en frontend, botón "Reponer" en dashboard.
- **Build T1-T5**: T1 modelo Restock+db init, T2 API POST/GET restocks+tests, T3 frontend vista restocks+hash routing, T4 botón "Reponer" en dashboard, T5 E2E tests+docs README+validate.sh.
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 81 passed ✅ boot /health 200 ✅. Push a GitHub OK con tag `F05`.

## 2026-09-15 — F06: Proveedores / Órdenes de Compra ✅
- **Decisión stack & arquitectura**: ADR-007. Modelo `Supplier` y `PurchaseOrder` añadidos vía `create_all`. Nueva FK opcional `restocks.purchase_order_id` para trazabilidad. Recepción de orden atómica: crea `Restock`, incrementa `Product.stock`, actualiza `qty_received` y `status` (`partial`/`received`). Frontend multi-página extendido: vista `#/suppliers` (CRUD proveedores), vista `#/purchase-orders` (CRUD órdenes, modal recepción iterativa, botón cancelar, filtros, badges estado), botón "Reponer" en dashboard que navega a `#/restocks` pre-seleccionando producto.
- **Estructura**: `app/models/supplier.py`, `app/models/purchase_order.py`, `app/api/routes/suppliers.py`, `app/api/routes/purchase_orders.py`, `app/models/restock.py` (FK opcional `purchase_order_id`), `app/tests/test_suppliers.py`, `app/tests/test_purchase_orders.py`, vistas frontend en `app/static/` con modales recepción/cancelación, badges de estado, filtros, botón "Reponer" en dashboard.
- **Build T1-T7**: T1 modelos Supplier+PurchaseOrder+DB init, T2 API CRUD Suppliers+tests, T3 API CRUD PurchaseOrders+endpoint receive atómico+tests, T4 frontend Suppliers, T5 frontend PurchaseOrders+modales receive/cancel, T6 integración Dashboard/Restocks (botón Reponer + enlaces PO↔Restock), T7 E2E tests+docs README+validate.sh.
- **Verificación final**: `./validate.sh` → ruff ✅ mypy ✅ pytest 135 passed ✅ boot /health 200 ✅. Push a GitHub OK con tag `F06`.