# Feature F05: Entradas / Reposición de Stock con Historial

## Descripción
Permite registrar reposiciones de stock, actualizar la cantidad disponible de productos y mantener un historial de entradas.

## Modelo de datos
- **restocks**
  - `id`: PK
  - `product_id`: FK → products.id
  - `qty`: int > 0
  - `unit_cost_cents`: int (opcional)
  - `total_cost_cents`: int (opcional, calculado como `qty * unit_cost_cents`)
  - `notes`: str (opcional)
  - `created_at`: datetime (auto)

## API REST
- `POST /api/restocks`
  - Body: `{product_id, qty, unit_cost_cents?, notes?}`
  - Respuestas: 201 (creado), 404 (producto no existe), 422 (qty <= 0)
  - Acción: crea registro y **incrementa** `Product.stock` en la misma transacción.
- `GET /api/restocks`
  - Lista de reposiciones, ordenado DESC por `created_at`.

## Frontend
- Sidebar: enlace `#/restocks`.
- Vista `#view-restocks`:
  - Formulario: selector de producto, qty, unit_cost_cents, notes.
  - Tabla historial: ID, Producto, Cantidad, Costo Unit., Costo Total, Notas, Fecha.
- Dashboard: botón "Reponer" en filas de bajo stock que redirige a `#/restocks` con producto pre‑seleccionado.
