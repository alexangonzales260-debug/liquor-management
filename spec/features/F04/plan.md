# Plan de Implementación para F04 - Gestión de Categorías

### 1. Modelo de datos
- Añadir clase `Category` en `models.py` con campos `id: int PK`, `name: str` (unique, not empty), `description: Optional[str]`, `created_at: datetime` (default now).
- Actualizar `init_db()` para incluir `Category` en `SQLModel.metadata.create_all`.

### 2. API REST (`/api/categories`)
- Crear router `categories_router` en `routers/categories.py`.
- Endpoints:
  - `GET /api/categories` → lista ordenada alfabéticamente.
  - `POST /api/categories` → crear, validar unicidad y no vacío.
  - `GET /api/categories/{id}` → detalle o 404.
  - `PUT /api/categories/{id}` → actualizar con validaciones.
  - `DELETE /api/categories/{id}` → borrar solo si no hay productos asociados.
- Incluir pruebas unitarias en `tests/test_categories.py`.

### 3. Frontend
- Añadir enlace en `sidebar.html` a `#/categories`.
- Crear vista `#view-categories` en `static/js/app.js` con formulario y tabla.
- Modificar `#view-products`:
  - Reemplazar campo `#category` por `<select>` poblado vía fetch a `/api/categories`.
  - Añadir filtro de categoría que reutiliza la lista.

### 4. Integración y E2E
- Actualizar `e2e/tests/categories.test.js` para cubrir CRUD vía UI.
- Ajustar `validate.sh` para incluir nuevos tests.

### 5. Documentación
- Actualizar `README.md` sección API con ejemplos de categorías.
- Añadir notas de migración (no hay migraciones, solo `create_all`).