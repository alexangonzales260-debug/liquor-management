# F06 — Proveedores / Órdenes de Compra

Estado: Aprobado (Plan Mode)
Sprint: F06
Features base: F01–F05
Stack: FastAPI + SQLModel + SQLite, frontend existente (vistas hash `#/`)

---

## 1. Objetivo

Añadir la gestión de **proveedores (Suppliers)** y **órdenes de compra (PurchaseOrders)** al gestor de licores, de modo que sea posible:

- Registrar y mantener un catálogo de proveedores.
- Crear órdenes de compra por producto y proveedor.
- Recibir parcial o totalmente una orden mediante un endpoint de recepción que, de forma **atómica**, crea un `Restock`, actualiza `qty_received`, `status` y `Product.stock`.

No se incorporan dependencias nuevas. Las nuevas tablas se crean a través de `SQLModel.create_all` en `init_db` (patrón existente de F01–F05).

---

## 2. Modelos de datos

Todas las tablas nuevas registran `created_at` con UTC. Convenciones de dinero: **centavos (int)**.

### 2.1 `Supplier` (tabla `suppliers`)

| Campo            | Tipo      | Reglas                                   |
|------------------|-----------|------------------------------------------|
| `id`             | int (PK)  | Autoincremental                          |
| `name`           | str       | `unique`, `index`, requerido, no vacío   |
| `contact_person` | str \| None | Opcional                               |
| `email`          | str \| None | Opcional, opcionalmente validado        |
| `phone`          | str \| None | Opcional                                |
| `address`        | str \| None | Opcional                                |
| `tax_id`         | str \| None | Opcional (RFC/NIT, no único)            |
| `notes`          | str \| None | Opcional                                |
| `created_at`     | datetime    | Default UTC                              |

Relaciones:
- 1 Supplier → N PurchaseOrder (`purchase_orders`).
- `Supplier.orders` (relationship, back_populates en `PurchaseOrder`).

### 2.2 `PurchaseOrder` (tabla `purchase_orders`)

| Campo             | Tipo        | Reglas                                   |
|-------------------|-------------|------------------------------------------|
| `id`              | int (PK)    | Autoincremental                          |
| `supplier_id`     | int (FK)    | → `suppliers.id`, `ondelete=RESTRICT`    |
| `product_id`      | int (FK)    | → `products.id`, `ondelete=RESTRICT`     |
| `qty_ordered`     | int         | `gt=0`                                   |
| `qty_received`    | int         | Default `0`, `ge=0`, ≤ `qty_ordered`     |
| `unit_cost_cents` | int         | `ge=0` (coste unitario de compra)        |
| `total_cost_cents`| int         | Calculado `= unit_cost_cents * qty_ordered` |
| `status`          | Enum        | `pending` / `partial` / `received` / `cancelled` (default `pending`) |
| `order_date`      | date        | Default hoy, requerido                   |
| `expected_date`   | date \| None | Opcional                                |
| `received_date`   | date \| None | Opcional (se fija al completar recepción) |
| `notes`           | str \| None | Opcional                                 |
| `created_at`      | datetime    | Default UTC                              |

Transiciones de `status` (solo vía recepción o cancelación):
- `pending + qty_received == 0` → `received` (recepción total), `partial` (recepción parcial).
- `partial` → `received` (recepción completa) o se mantiene `partial`.
- `pending`/`partial` → `cancelled` (cancelación manual).
- `received` y `cancelled` son terminales: no aceptan recepciones.

### 2.3 Modelo opcional: `Restock.purchase_order_id`

FK opcional y nullable en `Restock` (tabla `restocks`) → `purchase_orders.id`, para trazabilidad del lote creado por cada recepción.

- `nullable=True`, sin break de los `Restock` existentes (migración ligera de modelo, `create_all` añade la columna).
- `PurchaseOrder.restock` (relationship hacia el Restock generado).

---

## 3. API REST

Prefijo raíz: `/api`.

### 3.1 `/api/suppliers`

| Método | Ruta             | Descripción                                                |
|--------|------------------|------------------------------------------------------------|
| GET    | `/api/suppliers` | Lista proveedores. Filtros query: `q` (búsqueda por nombre/contacto), `sort` (`name`/`created_at`, default `name`), paginación si ya existe en el proyecto. |
| GET    | `/api/suppliers/{id}` | Detalle de un proveedor (incluye conteo de órdenes).    |
| POST   | `/api/suppliers` | Crea proveedor. 422 si `name` ya existe.                 |
| PUT    | `/api/suppliers/{id}` | Actualiza proveedor (actualización parcial con PATCH). |
| DELETE | `/api/suppliers/{id}` | Elimina proveedor solo si **no tiene órdenes** (integridad referencial). Si tiene órdenes → `409 Conflict` con detalle. |

Esquemas Pydantic/SQLModel:
- `SupplierCreate`: `name` (obligatorio), resto opcional.
- `SupplierUpdate`: todos opcionales; validar nombre único en update.
- `SupplierRead`: todos los campos + `order_count`.

### 3.2 `/api/purchase-orders`

| Método  | Ruta                          | Descripción                                               |
|---------|-------------------------------|-----------------------------------------------------------|
| GET     | `/api/purchase-orders`        | Lista órdenes. Filtros: `supplier_id`, `product_id`, `status`, `q`. |
| GET     | `/api/purchase-orders/{id}`   | Detalle con `supplier` y `product` embebidos (join info). |
| POST    | `/api/purchase-orders`        | Crea orden. Valida `supplier_id` y `product_id` existen; calcula `total_cost_cents`. |
| PUT     | `/api/purchase-orders/{id}`   | Actualiza orden (solo si `status == pending`; no permite bajar `qty_received` por debajo de lo recibido ni reducir `qty_ordered < qty_received`). |
| DELETE  | `/api/purchase-orders/{id}`   | Elimina solo si `status == pending` (sin recepciones). Con recepción/estado avanzado → `409`. |
| POST    | `/api/purchase-orders/{id}/receive` | **Recepción parcial/total** — ver §3.3. |
| POST    | `/api/purchase-orders/{id}/cancel` | Cancela orden si no está `received`/`cancelled` (opcional, puede ir en PUT status). |

### 3.3 Endpoint `POST /api/purchase-orders/{id}/receive`

Body: `{"qty_received": int > 0}` (cantidad adicional a recibir).

Lógica (todo dentro de una **transacción / lock por fila** para atomicidad):

1. Cargar orden con `FOR UPDATE` (o `with_for_update` si SQLite lo permite) o validación dentro del repositorio.
2. Validar que exista la orden → 404.
3. Validar `status` en `{pending, partial}` → de lo contrario 409.
4. Validar `qty_received_nueva <= qty_ordered - qty_received_actual` → de lo contrario 400/422.
5. Si `qty_ordered - qty_received == 0` → 400 (no hay nada pendiente).
6. **Crear `Restock`**: `product_id`, `quantity = qty_nueva`, `unit_cost_cents = unit_cost_cents` (o con `source=restock` si el modelo tiene campo), `purchase_order_id = order.id`.
7. **Actualizar `Product.stock += qty_nueva`** (recalcular; usar UPDATE atómico si el modelo lo soporta).
8. **Actualizar `qty_received += qty_nueva`**.
9. **Actualizar `status`**:
   - Si `qty_received == qty_ordered` → `received` y `received_date = today`.
   - Si `qty_received > 0` y `< qty_ordered` → `partial`.
   - Si es la primera recepción y queda pendiente → `partial`.
10. Devolver `PurchaseOrderRead` actualizado + detalle del Restock creado.

Devolver 201 si se crea un `Restock` nuevo, o el orden con `201`/`200` según decisión del proyecto (definir en implementación). No se permite recibir cantidad cero.

### 3.4 Reglas de integridad globales

- `DELETE /api/suppliers/{id}`: si existe `PurchaseOrder` con ese `supplier_id` → 409.
- `DELETE /api/purchase-orders/{id}`: si `qty_received > 0` o `status != pending` → 409.
- Recalcular `total_cost_cents` en cada `POST`/`PUT`.
- No exponer datos sensibles; mensajes de error coherentes con el resto de la API.

---

## 4. Frontend

Vistas hash existentes (`#/...`). Se añaden:

### 4.1 Sidebar

Enlaces nuevos:
- `#/suppliers` — "Proveedores"
- `#/purchase-orders` — "Órdenes de compra"

Siguen el mismo patrón y estilo que los enlaces actuales de productos/ventas/restocks.

### 4.2 Vista Proveedores

- Listado de proveedores (tabla) con acciones: ver/editar/eliminar.
- Formulario modal de alta/edición (mismo patrón que CRUD de productos).
- Búsqueda/filtro por texto.
- Al intentar eliminar un proveedor con órdenes, mostrar el error 409 de la API.
- Vista de detalle con conteo de órdenes y acceso a sus órdenes.

### 4.3 Vista Órdenes de Compra

- Listado de órdenes con columnas: Id, Proveedor, Producto, Cant. pedida, Recibida, Costo unitario, Total, Estado, Fechas.
- Filtros: por proveedor, estado, texto.
- Formulario modal de alta: selección de proveedor, producto, cantidades, costos, fechas.
- **Modal de recepción**: input de cantidad a recibir (parcial/total), muestra pendiente disponible, confirma → POST `/receive`.
- Acción de cancelar orden pendiente.
- Indicador visual de estado (badge de color por status).
- Guard contra reducción de cantidades ya recibidas.

### 4.4 Integración con Dashboard / Restocks

- La vista de Restocks muestra los nuevos restocks generados por recepción (origen `purchase_order_id`).
- El Dashboard (si enumera producto bajo stock) se beneficia de que `Product.stock` se actualice en recepción.
- Enlaces desde `#/restocks` hacia la orden de compra que originó el restock (si el campo opcional está implementado).

---

## 5. Reglas de negocio consolidadas

| Regla | Descripción |
|-------|-------------|
| Nombre de proveedor único | No se permite crear dos `Supplier` con el mismo `name` (case-insensitive). |
| Cantidad positiva | `qty_ordered > 0`; `qty_received` entre 0 y `qty_ordered`. |
| Recepción ≤ pendiente | No recibir más de lo pedido. |
| Estados terminales | `received` y `cancelled` no admiten recepciones ni ediciones. |
| Solo edición de pendientes | Editar/eliminar orden solo si `status == pending`. |
| Trazabilidad | Cada recepción genera un `Restock` con referencia `purchase_order_id`. |
| Coste calculado | `total_cost_cents = qty_ordered * unit_cost_cents`, nunca manual. |

---

## 6. Almacenamiento y boot

- `init_db()` ejecuta `SQLModel.metadata.create_all(engine)` y crea `suppliers`, `purchase_orders` y la columna nueva `restocks.purchase_order_id`.
- Sin migraciones externas (Alembic no disponible); `create_all` crea tablas nuevas y columnas nuevas sin tocar tablas existentes.
- `validate.sh` (ruff + mypy + pytest + boot check) debe pasar tras F06.

---

## 7. Criterios de aceptación

1. `GET /api/suppliers` y CRUD completo funcionan; DELETE con órdenes devuelve 409.
2. `GET /api/purchase-orders` y CRUD; `POST /{id}/receive` crea Restock, incrementa stock, actualiza `qty_received` y `status`.
3. Las tablas `suppliers`, `purchase_orders` y `restocks.purchase_order_id` existen tras `init_db`.
4. El frontend permite gestionar proveedores y órdenes, y recibir mercancía.
5. `./validate.sh` pasa.
6. Sin dependencias nuevas.