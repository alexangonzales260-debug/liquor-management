# F06 — Plan de implementación

Objetivo: Proveedores y Órdenes de Compra. Cada componente se implementa y verifica de forma incremental; al final se ejecuta `./validate.sh`.

---

## Fase 0 — Preparación e inventario (antes de codificar)

- Leer estructura actual: modelos (`Product`, `Category`, `Sale`, `Restock`), `init_db`, router de API, frontend (sidebar, vistas `#/...`), `validate.sh`.
- Confirmar convenciones: pydantic v2 vs v1, manejo de rutas (`APIRouter`), patrones de repositorio/servicio, `money_cents`, `from __future__ import annotations`.
- Identificar archivos de modelos, schemas, routers, servicios y el router principal de API.

---

## Fase 1 — Modelos y base de datos

Archivos: modelos `supplier` y `purchase_order`, edición de `restock`, registro en `init_db`.

1. Crear `Supplier` (tabla `suppliers`).
2. Crear `PurchaseOrder` (tabla `purchase_orders`), con enum `PurchaseOrderStatus`.
3. Añadir FK opcional `purchase_order_id` a `Restock` (nullable) y relationship.
4. Registrar ambos modelos en `init_db` y en imports centrales para que `create_all` las cree.
5. Verificar boot: la app arranca y las 3 tablas existen (consulta vía shell/tests).

Check: `./validate.sh` (o al menos boot check + mypy) tras cada commit.

---

## Fase 2 — API de Suppliers

1. Schemas: `SupplierCreate`, `SupplierUpdate`, `SupplierRead` (+ `order_count`).
2. Router `GET /api/suppliers` (filtros `q`, `sort`).
3. Router `GET /api/suppliers/{id}` (detalle con `order_count`).
4. Router `POST /api/suppliers` (validación de nombre único → 422).
5. Router `PUT/PATCH /api/suppliers/{id}` (nombre único en update).
6. Router `DELETE /api/suppliers/{id}` (bloqueo 409 si tiene órdenes).
7. Registrar router en la app; tests de CRUD + 409.

---

## Fase 3 — API de Purchase Orders + recepción

1. Schemas: `PurchaseOrderCreate`, `PurchaseOrderUpdate`, `PurchaseOrderRead` (con supplier/product embebidos), `ReceiveRequest`.
2. Router `GET /api/purchase-orders` (filtros `supplier_id`, `product_id`, `status`, `q`).
3. Router `GET /api/purchase-orders/{id}` (detalle).
4. Router `POST /api/purchase-orders` (valida FKs, calcula `total_cost_cents`).
5. Router `PUT /api/purchase-orders/{id}` (solo pendiente, no reducir recibido).
6. Router `DELETE /api/purchase-orders/{id}` (solo pendiente sin recepciones → 409 en otro caso).
7. **Router `POST /api/purchase-orders/{id}/receive`** (lógica transaccional §3.3).
8. (Opcional) Router `POST /api/purchase-orders/{id}/cancel`.
9. Registrar router en la app; tests: recepción parcial → `partial`, total → `received` + stock + Restock creado; recepción sobre recibida → error; recepción sobre `received`/`cancelled` → 409.

---

## Fase 4 — Frontend: Proveedores

1. Añadir enlace `#/suppliers` en el sidebar.
2. Vista de listado de proveedores con búsqueda.
3. Formulario modal alta/edición (reutiliza patrón de CRUD existente).
4. Eliminar con manejo de error 409 (mensaje claro).
5. Verificación manual + tareas de JS (pasar linters/covs del frontend si existen en `validate.sh`).

---

## Fase 5 — Frontend: Órdenes de Compra + recepción

1. Añadir enlace `#/purchase-orders` en el sidebar.
2. Vista de listado de órdenes con filtros por proveedor/estado.
3. Formulario modal alta (selects de proveedor y producto).
4. Modal de recepción (cantidad a recibir, pendiente disponible).
5. Acción de cancelar orden.
6. Badges/estado visual y guard de edición de canceladas/recibidas.

---

## Fase 6 — Integración Dashboard / Restocks

1. Mostrar en `#/restocks` el origen `purchase_order_id` (columna "Orden" y link).
2. Ajustar Dashboard/logica de stock si es necesario para reflejar stock actualizado.
3. Navegación cruzada: de restock a orden de compra; de proveedor a sus órdenes.

---

## Fase 7 — E2E, documentación y validate

1. Pruebas end-to-end del flujo completo: crear proveedor → crear orden → recibir → stock incrementado → restock con trazabilidad.
2. Actualizar documentación/README si el repo lo requiere.
3. Ejecutar `./validate.sh` completo y corregir hasta que pase.
4. Revisar que no se añadieron dependencias nuevas.

---

## Orden de commits sugerido

T1 → T2 → T3 → T4 → T5 → T6 → T7 (ver `tasks.md`). Cada tarea debe dejar el proyecto en estado funcional y con `./validate.sh` en verde cuando aplique.