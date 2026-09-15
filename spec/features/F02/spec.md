# F02 Specification

## Context & Goal
Provide a minimal HTML/JS frontend for the F01 products CRUD API, served directly by FastAPI. Users can list, create, edit and delete liquor products and filter them by category and name search, all without a SPA framework or build tooling.

## Stack
- **FastAPI StaticFiles** mounted at `/static` (CSS + JS, no build step).
- **index.html** served at `/` (root).
- **Plain CSS** (`style.css`) and **vanilla JS** (`app.js`) using `fetch`.
- Reuses the existing API at `/api/products` (no auth, no new dependencies).

## UI Acceptance Criteria
- **List products** in a table with columns: `name`, `category`, `volume_ml` (suffixed with ` ml`), `price_cents` (formatted as currency, e.g. `$12.99`), `stock`.
- **Create product**: form with fields `name` (required), `category` (optional), `volume_ml`, `price_cents`, `stock`. Validation: `name` non-empty; `volume_ml`, `price_cents`, `stock` as non-negative integers; on invalid input the form shows a message and no request is sent.
- **Edit product**: clicking Edit loads the product into the form (pre-filled) and switches the submit to a `PUT /api/products/{id}`.
- **Delete product**: clicking Delete asks for confirmation (native confirm dialog); on accept sends `DELETE /api/products/{id}` and removes the row from the table.
- **Filters**: a search input (`name` substring) and a category input/select; triggering a filter calls `GET /api/products?category=...&search=...` reusing the API query params and re-renders the table.
- **Loading state**: a visible indicator while any fetch is in flight.
- **Error/empty states**: fetch errors show a message and keep last known state; 4xx responses display the API `detail` to the user (e.g. 404/422); empty results render "no products" row.
- After create/update the list is refreshed from the API (source of truth).

## File Structure
```
app/static/
├── index.html     # table, filter bar, form, status/error area
├── style.css      # minimal clean styling
└── app.js         # fetch logic, rendering, form actions
app/main.py        # (edit) mount StaticFiles + root route
app/tests/test_frontend.py  # (new) E2E via TestClient
```

## Out of Scope
- Authentication, SPA framework, build tools/bundlers, dashboard, low-stock alerts, pagination, separate frontend server. No new Python dependencies.