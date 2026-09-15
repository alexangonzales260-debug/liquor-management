# F02 Plan

## Tech Stack
- **FastAPI** — serves `index.html` at `/` via `FileResponse` and mounts `StaticFiles` at `/static`.
- **Existing CRUD API** `/api/products` — all data operations; no new backend features.
- **Vanilla HTML/CSS/JS** — fetched with `fetch`, rendered with `innerHTML`/DOM, no framework, no build step.
- **No new dependencies** — `fastapi`, `pytest`, `httpx` (already present) are enough; `validate.sh` stays the single gate.

## Directory Structure (to create / touch)
```
app/
├── main.py                  # (touch) mount StaticFiles("/static") + root "/" that returns index.html
├── static/                  # (create)
│   ├── index.html           # #products-table, #filters, #product-form, #status
│   ├── style.css
│   └── app.js
└── tests/
    ├── conftest.py          # (touch) make TestClient lifecycle compatible with StaticFiles
    └── test_frontend.py     # (create) E2E: root serves HTML, /static assets load
validate.sh                  # must stay green
```

Design decision: frontend logic in `app.js` reads the list, handles form create/edit, delete confirmation, filters and error rendering. The only backend change is mounting static files and a root route — everything else reuses F01 APIs.

## Atomic Tasks
| Task | Description | Commit |
|------|-------------|--------|
| T1 | Mount `StaticFiles` at `/static` + root `/` serving `index.html`; skeleton HTML/CSS with empty table, filter bar, form. E2E test that `/` returns HTML and assets load. | `feat(f02): static files & index skeleton` |
| T2 | `app.js`: `GET /api/products` with `category` & `search` params, render table, loading + error + empty states. | `feat(f02): list products & filters` |
| T3 | Create + edit: form validation, `POST`, pre-fill on edit, `PUT`, refresh list after save. | `feat(f02): create & edit products` |
| T4 | Delete (confirm + `DELETE`), UX/styling polish, currency formatting. | `feat(f02): delete & ux polish` |
| T5 | Full E2E test suite (`test_frontend.py`) covering all UI states; run `validate.sh` green. | `feat(f02): frontend e2e tests` |

Justification for order: T1 establishes serving static files (precondition for everything); T2/T3 build the core flows read→create/edit; T4 finishes destructive action + presentation; T5 locks behavior with `validate.sh` as the exit gate (CONSTRAINTS.md: validate.sh is the only gate).