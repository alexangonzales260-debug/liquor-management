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