# Tasks – F05

- [ ] **T1** – Modelo `Restock` + init_db
  - Definir clase `Restock` en `models.py` con validación de cantidades.
  - Registrar en `init_db` para que `create_all` cree la tabla.

- [ ] **T2** – API REST `/api/restocks`
  - Crear rutas con `POST` y `GET`.
  - Implementar transacción que incremente `Product.stock`.
  - Tests unitarios: 201, 404, 422, y verificación del incremento de stock.

- [ ] **T3** – Vista frontend `#view-restocks`
  - Enlace en sidebar.
  - Formulario de reposición (producto, qty, costo unit., notas).
  - Tabla de historial de entradas.

- [ ] **T4** – Integración botón "Reponer" en dashboard
  - Botón en filas de bajo stock que navegue a `#/restocks` pre‑seleccionando producto.

- [ ] **T5** – E2E + docs + validate.sh
  - Test E2E del flujo completo.
  - Actualizar README.
  - Ejecutar y asegurar `./validate.sh` pasa.