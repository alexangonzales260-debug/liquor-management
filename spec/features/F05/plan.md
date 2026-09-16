# Plan de Implementación – F05

1. **Modelo de datos**
   - Crear tabla `restocks` en `models.py` con campos según spec.
   - Extender `init_db` para crear la nueva tabla (usa `SQLModel.metadata.create_all`).

2. **API REST**
   - Implementar `POST` y `GET` en `routes/restocks.py`.
   - Usar transacción para crear restock y actualizar `Product.stock`.
   - Validar existencia de producto y cantidad > 0.

3. **Frontend**
   - Añadir enlace `#/restocks` en sidebar (`templates/index.html`).
   - Crear vista `#view-restocks` con formulario y tabla (HTML + JS).
   - Obtener lista de productos para el select mediante `GET /api/products`.
   - Renderizar historial de entradas.

4. **Integración en Dashboard**
   - Modificar tabla de bajo stock en `#view-dashboard` para incluir botón "Reponer".
   - Al pulsar, redirigir a `#/restocks` y pre‑seleccionar el producto en el select.

5. **Tests y validación**
   - Tests unitarios para la API (POST, GET) cubriendo 201, 404, 422 y actualización de stock.
   - Test de integración E2E para flujo completo de reposición.
   - Actualizar `README` con instrucciones de uso y documentación del nuevo endpoint.
   - Verificar que `./validate.sh` pasa (ruff, mypy, pytest, boot check).