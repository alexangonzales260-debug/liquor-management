# Liquor Management

API de gestión de inventario de licores, construida con FastAPI + SQLModel sobre una base SQLite. Permite administrar productos (altas, bajas, consultas y ediciones) con validación de datos, tests aislados y un script único de calidad.

## Requisitos

- Python **3.11+**

## Instalación

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Cómo correr

```bash
uvicorn app.main:app --reload
```

La API queda disponible en <http://localhost:8000> y su documentación interactiva en <http://localhost:8000/docs>.

## Cómo testear

Puerta única de calidad (lint + typecheck + tests + arranque):

```bash
./validate.sh
```

O bien los tests aislados:

```bash
.venv/bin/pytest app/tests -v
```

## API endpoints

| Método | Ruta                     | Descripción                                        |
| ------ | ------------------------ | -------------------------------------------------- |
| GET    | `/health`                | Health check de la API (`{"status": "ok"}`)        |
| GET    | `/api/products`          | Lista productos (filtros: `category`, `search`)    |
| POST   | `/api/products`          | Crea un producto                                   |
| GET    | `/api/products/{id}`     | Devuelve un producto por id                        |
| PUT    | `/api/products/{id}`     | Reemplaza un producto por id                       |
| DELETE | `/api/products/{id}`     | Elimina un producto por id (204)                   |
| GET    | `/api/categories`        | Lista categorías (con `products_count`)            |
| POST   | `/api/categories`        | Crea una categoría                                 |
| GET    | `/api/categories/{id}`   | Devuelve una categoría por id                      |
| PUT    | `/api/categories/{id}`   | Reemplaza una categoría por id (propaga el nombre a sus productos) |
| DELETE | `/api/categories/{id}`   | Elimina una categoría por id (204); 400 si tiene productos |
| POST   | `/api/restocks`          | Registra una reposición (incrementa el stock del producto; calcula `total_cost_cents` si se envía `unit_cost_cents`; acepta `notes` opcionales) |
| GET    | `/api/restocks`          | Lista el historial de reposiciones (ordenado por fecha desc) |
| GET    | `/api/suppliers`         | Lista proveedores (búsqueda por `q`; ordenable por `name` o `created_at`) |
| POST   | `/api/suppliers`         | Crea un proveedor; `422` si el nombre ya existe |
| GET    | `/api/suppliers/{id}`    | Devuelve un proveedor por id (con `order_count`) |
| PUT    | `/api/suppliers/{id}`    | Actualiza un proveedor por id |
| DELETE | `/api/suppliers/{id}`    | Elimina un proveedor por id (204); `409` si tiene órdenes asociadas |
| GET    | `/api/purchase-orders`   | Lista órdenes de compra (filtros: `supplier_id`, `product_id`, `status`, `q`) |
| POST   | `/api/purchase-orders`   | Crea una orden de compra (estado inicial `pending`) |
| GET    | `/api/purchase-orders/{id}` | Devuelve una orden por id (incluye `restock_ids`) |
| PUT    | `/api/purchase-orders/{id}` | Actualiza una orden (solo `pending`; permite `status: "cancelled"`) |
| DELETE | `/api/purchase-orders/{id}` | Elimina una orden (204); `409` si tiene stock recibido |
| POST   | `/api/purchase-orders/{id}/receive` | Recibe mercancía (crea un Restock e incrementa el stock) |

### `POST /api/restocks`

Body de ejemplo:

```json
{
  "product_id": 1,
  "qty": 5,
  "unit_cost_cents": 12000,
  "notes": "Reabastecimiento de fin de mes"
}
```

- `qty` es obligatorio y debe ser mayor a 0.
- `unit_cost_cents` es opcional (mayor o igual a 0). Si se envía, la API calcula `total_cost_cents = qty * unit_cost_cents`.
- `notes` es opcional.
- Responde `201` con la reposición creada e incrementa `stock` del producto. `404` si el producto no existe y `422` si la validación falla.

Respuesta de ejemplo:

```json
{
  "id": 1,
  "product_id": 1,
  "qty": 5,
  "unit_cost_cents": 12000,
  "total_cost_cents": 60000,
  "notes": "Reabastecimiento de fin de mes",
  "created_at": "2026-09-15T10:00:00"
}
```

### `POST /api/suppliers`

Body de ejemplo:

```json
{
  "name": "Distribuidora Central",
  "contact_person": "Ana Pérez",
  "email": "ana@central.com",
  "phone": "555-0100",
  "tax_id": "RFC-123",
  "notes": "Pago a 30 días"
}
```

- `name` es obligatorio y único (case-insensitive); duplicados responden `422`.
- El resto de campos son opcionales (`contact_person`, `email`, `phone`, `address`, `tax_id`, `notes`).
- Responde `201` con el proveedor creado, incluyendo `order_count` (0 inicialmente).
- `GET /api/suppliers?q=<texto>` filtra por nombre o persona de contacto; `GET /api/suppliers?sort=created_at` cambia el orden.
- `DELETE /api/suppliers/{id}` responde `409` si el proveedor tiene órdenes de compra asociadas.

### `POST /api/purchase-orders`

Body de ejemplo:

```json
{
  "supplier_id": 1,
  "product_id": 2,
  "qty_ordered": 10,
  "unit_cost_cents": 12000,
  "expected_date": "2026-10-01",
  "notes": "Parada semanal"
}
```

- `supplier_id`, `product_id`, `qty_ordered` (mayor a 0) y `unit_cost_cents` son obligatorios.
- El endpoint calcula `total_cost_cents = qty_ordered * unit_cost_cents` y deja la orden en estado `pending`.
- `expected_date` y `notes` son opcionales.
- Responde `201` con la orden creada (incluye `supplier_name`, `product_name` y `restock_ids`). `404` si el proveedor o producto no existe y `422` si la validación falla.

### `POST /api/purchase-orders/{id}/receive`

Body de ejemplo:

```json
{
  "qty_received": 4
}
```

- Recibe mercancía de una orden `pending` o `partial`. `qty_received` debe ser mayor a 0 y no superar la cantidad pendiente (`qty_ordered - qty_received`).
- Al recibir, crea un `Restock` vinculado a la orden (`purchase_order_id`), incrementa el stock del producto y actualiza `qty_received` de la orden.
- Si `qty_received` iguala `qty_ordered`, la orden pasa a estado `received` y se asigna `received_date`; si no, el estado queda en `partial`.
- Responde `201` con `{ "po": {...}, "restock_id": <id> }`. `400` si excede la cantidad pendiente, `409` si la orden no está `pending`/`partial` (ej. ya recibida o cancelada) y `404` si la orden no existe.
- `PUT /api/purchase-orders/{id}` solo funciona sobre órdenes `pending` y permite `{"status": "cancelled"}` para cancelar; `DELETE` responde `409` si la orden tiene stock recibido.
- `GET /api/purchase-orders` acepta los filtros `supplier_id`, `product_id`, `status` y `q` (busca por nombre de proveedor o producto).

## Vistas (frontend)

La interfaz es de una sola página con rutas por hash (`#/...`):

| Ruta           | Vista                                              |
| -------------- | -------------------------------------------------- |
| `#/suppliers`   | Gestión de proveedores (crear, editar y eliminar)     |
| `#/purchase-orders` | Órdenes de compra con filtros, modal de recepción, botón cancelar y badges de estado |

### Proveedores (`#/suppliers`)

Muestra una tabla con todos los proveedores (nombre, contacto, email, teléfono, dirección) y un formulario completo para crear/editar (incluye `tax_id` y notas). Cada fila ofrece acciones **Editar** y **Eliminar**; al eliminar un proveedor con órdenes asociadas se muestra el error de la API.

### Órdenes de compra (`#/purchase-orders`)

- **Filtros**: por estado (`pending`, `partial`, `received`, `cancelled`), por proveedor y búsqueda libre sobre producto o proveedor, con botones **Aplicar** y **Limpiar**.
- **Recibir**: las órdenes `pending` y `partial` muestran el botón **Recibir**, que abre un modal para indicar la cantidad a recibir (pre-cargado con la cantidad pendiente). Al confirmar, la API crea el Restock, incrementa el stock y el badge de estado cambia (`partial` o `received`).
- **Cancelar**: las órdenes `pending` muestran un botón **Cancelar** con confirmación (modal); las órdenes canceladas no admiten recepción.
- **Badges de estado**: el estado se muestra con `status-badge` de colores por estado (`Pendiente`, `Parcial`, `Recibida`, `Cancelada`).
- Las órdenes con reposiciones enlazan a **Ver reposición** (`#/restocks?po=<id>` y la fila se resalta). A su vez, la tabla de `#/restocks` muestra en la columna **Orden** un enlace `#/purchase-orders?po=<id>` hacia la orden que generó una reposición.

### Dashboard → Reponer

En el dashboard, cada producto con stock bajo muestra un botón **Reponer** (`restock-btn`): al pulsarlo navega a `#/restocks` con el producto pre-seleccionado en `restock-product` para registrar la entrada (cantidad, costo unitario y notas opcionales).