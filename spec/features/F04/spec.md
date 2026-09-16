# Feature F04: Gestión de Categorías

## Objetivo
Agregar soporte completo para crear, leer, actualizar y eliminar categorías de licores, y exponer la API correspondiente.

## Requisitos
- Modelo `Category` con campos `id`, `name` (único, no vacío), `description` (opcional) y `created_at`.
- Endpoints REST bajo `/api/categories` con comportamientos descritos en el enunciado.
- Actualización de la vista de productos para usar un `<select>` de categorías y permitir filtrar por categoría.
- Enlace en la barra lateral a `#/categories`.

## Dependencias
- Ninguna nueva dependencia. Usar los paquetes existentes (`fastapi`, `sqlmodel`, etc.).