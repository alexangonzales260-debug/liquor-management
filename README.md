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

## Vistas (frontend)

La interfaz es de una sola página con rutas por hash (`#/...`):

| Ruta           | Vista                                              |
| -------------- | -------------------------------------------------- |
| `#/dashboard`  | KPIs y tabla de stock bajo                          |
| `#/products`   | CRUD y filtros de productos                         |
| `#/sales`      | Registro de ventas                                 |
| `#/categories` | Gestión de categorías (crear, editar y eliminar)    |
| `#/restocks`   | Registro de reposiciones e historial                |

En el dashboard, cada producto con stock bajo muestra un botón **Reponer**: navega a `#/restocks` con el producto pre-seleccionado para registrar la entrada (cantidad, costo unitario y notas opcionales).