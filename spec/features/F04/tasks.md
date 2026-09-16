# Tareas Atómicas para F04 - Gestión de Categorías

## T1: Modelo Category + init_db
- [ ] Crear clase `Category` en `app/models.py` con campos: id (PK), name (unique, not null), description (nullable), created_at (default datetime.now).
- [ ] Importar `Category` en `app/database.py` y añadir a `SQLModel.metadata.create_all`.
- [ ] Verificar que la tabla se crea al arrancar la app.

## T2: API CRUD Categorías + Tests Unitarios
- [ ] Crear `app/routers/categories.py` con router `categories_router`.
- [ ] Implementar 5 endpoints: GET list, POST create, GET by id, PUT update, DELETE.
- [ ] Validaciones: nombre único (400), nombre no vacío (422), DELETE bloqueado si hay productos (400).
- [ ] Registrar router en `app/main.py`.
- [ ] Escribir `tests/test_categories.py` con casos: crear, duplicado, vacío, leer, actualizar, borrar, borrar con productos asociados.

## T3: Frontend - Vista Categorías + Navegación Hash
- [ ] Editar `templates/sidebar.html`: añadir `<a href="#/categories">Categorías</a>`.
- [ ] En `static/js/app.js`: registrar ruta `#/categories` → función `renderCategoriesView()`.
- [ ] `renderCategoriesView()`:
  - Formulario (ID oculto, name requerido, description opcional, botón Guardar / Cancelar).
  - Tabla con columnas: ID, Nombre, Descripción, Acciones (Editar, Eliminar).
  - Fetch inicial a `/api/categories` para poblar tabla.
  - Handlers: submit form (POST o PUT), click Editar (llenar formulario), click Eliminar (confirm + DELETE).
  - Feedback toast/alert para éxito/error.

## T4: Integración Categorías en Vista Productos
- [ ] En `renderProductsView()` (static/js/app.js):
  - Cambiar input `#category` a `<select id="category">` con `<option value="">-- Sin categoría --</option>`.
  - Función `loadCategoriesSelect()` que hace fetch a `/api/categories` y rellena el select.
  - Llamar a `loadCategoriesSelect()` al montar la vista y antes de editar un producto.
  - Añadir filtro `<select id="filter-category">` sobre la tabla de productos que usa la misma lista.
  - Al filtrar, re-renderizar tabla solo con productos de esa categoría (o todos si vacío).

## T5: Tests E2E + validate.sh
- [ ] Crear `e2e/tests/categories.test.js` con Playwright/Puppeteer: navegar a `#/categories`, crear, editar, borrar, validar errores.
- [ ] Ampliar `e2e/tests/products.test.js` para verificar select y filtro de categoría funcionan.
- [ ] Ejecutar `./validate.sh` y confirmar que pasa (ruff, mypy, pytest, boot check).
- [ ] Documentar endpoints nuevos en `README.md` (sección API).