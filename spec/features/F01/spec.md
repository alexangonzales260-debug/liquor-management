# F01 Specification

**Context & Goal**: Provide a minimal CRUD API for managing liquor inventory items.

## Data Model (`products` table)
- `id`: integer PK, auto‑increment
- `name`: text, required
- `category`: text, optional
- `volume_ml`: integer, milliliters of the bottle
- `price_cents`: integer, price stored in cents to avoid floating‑point errors (e.g., $12.99 → 1299)
- `stock`: integer, units available
- `created_at`: timestamp, default now
- `updated_at`: timestamp, updated on change

## REST API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List products; optional query `category` and `search` (name substring) |
| POST | `/api/products` | Create product (JSON body) |
| GET | `/api/products/{id}` | Retrieve product detail |
| PUT | `/api/products/{id}` | Replace product entirely |
| DELETE | `/api/products/{id}` | Remove product |

## Acceptance Criteria
- All endpoints return correct HTTP status codes (200/201/204/400/404).
- Validation rejects missing required fields or negative numeric values.
- `price_cents` stored and returned as integer.
- List endpoint supports filtering by `category` and case‑insensitive name search.
- Database schema matches the model above.

## Out of Scope
- Sales processing, low‑stock alerts, dashboards, authentication, SPA frontend, reporting.
