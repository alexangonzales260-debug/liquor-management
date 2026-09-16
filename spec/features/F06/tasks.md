# F06 — Tareas atómicas (T1..T7)

Cada tarea = 1 commit. Toda tarea termina con el validador en verde (al menos boot/mypy/ruff), salvo indicación contraria.

## T1 — Modelos y base de datos

- [ ] Crear modelo `Supplier` (tabla `suppliers`).
- [ ] Crear modelo `PurchaseOrder` con `PurchaseOrderStatus` enum (tabla `purchase_orders`).
- [ ] Añadir FK `purchase_order_id` nullable a `Restock` + relationship.
- [ ] Registrar modelos en imports/`init_db` para que `create_all` cree las tablas.
- [ ] Verificar boot: app arranca, tablas `suppliers`, `purchase_orders` y columna en `restocks` existen.
- [ ] `./validate.sh` en verde.

## T2 — API de Suppliers

- [ ] Schemas `SupplierCreate`, `SupplierUpdate`, `SupplierRead` (con `order_count`).
- [ ] `GET /api/suppliers` (filtros `q`, `sort`).
- [ ] `GET /api/suppliers/{id}` (detalle + `order_count`).
- [ ] `POST /api/suppliers` (nombre único → 422).
- [ ] `PUT/PATCH /api/suppliers/{id}` (nombre único en update).
- [ ] `DELETE /api/suppliers/{id}` (409 si tiene órdenes).
- [ ] Registrar router en la app.
- [ ] Tests: CRUD, 422 por duplicado, 409 por eliminación con órdenes.
- [ ] `./validate.sh` en verde.

## T3 — API de Purchase Orders + recepción

- [ ] Schemas `PurchaseOrderCreate`, `PurchaseOrderUpdate`, `PurchaseOrderRead`, `ReceiveRequest`.
- [ ] `GET /api/purchase-orders` (filtros `supplier_id`, `product_id`, `status`, `q`).
- [ ] `GET /api/purchase-orders/{id}` (detalle con supplier/product).
- [ ] `POST /api/purchase-orders` (valida FK, calcula `total_cost_cents`).
- [ ] `PUT /api/purchase-orders/{id}` (solo `pending`, no reducir recibido).
- [ ] `DELETE /api/purchase-orders/{id}` (solo `pending` sin recepción; 409 en otro caso).
- [ ] `POST /api/purchase-orders/{id}/receive`:
  - [ ] Validar estado `{pending, partial}` (409 si `received`/`cancelled`).
  - [ ] Validar cantidad ≤ pendiente (400/422 si excede).
  - [ ] Crear `Restock` con `purchase_order_id` dentro de la misma transacción.
  - [ ] Incrementar `Product.stock`.
  - [ ] Actualizar `qty_received`, `status` y `received_date`.
- [ ] (Opcional) `POST /api/purchase-orders/{id}/cancel`.
- [ ] Tests: parcial → `partial`; total → `received`; stock OK; Restock creado; errores de cantidad/estado.
- [ ] `./validate.sh` en verde.

## T4 — Frontend: Proveedores

- [ ] Enlace `#/suppliers` en sidebar.
- [ ] Vista de listado de proveedores con búsqueda.
- [ ] Modal de alta/edición (patrón CRUD existente).
- [ ] Eliminar proveedor con manejo de error 409.
- [ ] Verificación manual del flujo.

## T5 — Frontend: Órdenes de Compra + recepción

- [ ] Enlace `#/purchase-orders` en sidebar.
- [ ] Vista de listado con filtros (proveedor, estado).
- [ ] Modal de alta de orden (selects proveedor/producto).
- [ ] Modal de recepción parcial/total (con pendiente disponible).
- [ ] Acción cancelar orden.
- [ ] Badges de estado y guards de edición para estados terminales.

## T6 — Integración Dashboard / Restocks

- [ ] Mostrar origen `purchase_order_id` en `#/restocks` con link a la orden.
- [ ] Navegación cruzada proveedor ↔ órdenes.
- [ ] Ajustes del Dashboard para reflejar stock/recepciones si aplica.

## T7 — E2E, documentación y validate

- [ ] Flujo E2E: crear proveedor → crear orden → recibir → verificar stock + Restock trazado.
- [ ] Actualizar documentación (README/docs) si el repo lo requiere.
- [ ] `./validate.sh` completo en verde (ruff + mypy + pytest + boot).
- [ ] Confirmar que no se añadieron dependencias nuevas.