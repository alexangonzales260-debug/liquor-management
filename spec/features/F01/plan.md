# F01 Plan

## Tech Stack
- **FastAPI** (0.115+) — web framework
- **SQLModel** — ORM built on SQLAlchemy + Pydantic (single model for DB & API)
- **SQLite** — file‑based DB (`inventory.db`)
- **Pydantic v2** — validation & serialization
- **pytest** + **httpx** (TestClient) — tests
- **ruff** — lint/format
- **mypy** — static type checking

## Minimal Dependencies
```
fastapi
uvicorn[standard]
sqlmodel
pytest
httpx
ruff
mypy
```

## Directory Structure (to create)
```
app/
├── main.py              # FastAPI app factory
├── config.py            # settings
├── database.py          # engine, session, init_db
├── models/
│   └── product.py       # SQLModel Product
├── schemas/
│   └── product.py       # Pydantic request/response (if separate)
├── api/
│   └── routes/
│       └── products.py  # CRUD endpoints
└── tests/
    ├── conftest.py      # test client fixture
    └── test_products.py # CRUD tests
validate.sh              # lint+typecheck+tests
README.md                # run instructions
```

## Atomic Tasks
| Task | Description | Commit |
|------|-------------|--------|
| T1 | Project skeleton: `pyproject.toml`, config, database, empty app | `feat(f01): project skeleton` |
| T2 | `Product` SQLModel + DB init + migration (create table) | `feat(f01): product model & db init` |
| T3 | CRUD endpoints in `api/routes/products.py` + wiring in `main.py` | `feat(f01): product CRUD endpoints` |
| T4 | Tests: list/create/read/update/delete + filters | `feat(f01): product CRUD tests` |
| T5 | `validate.sh` (ruff+mypy+pytest), README with run steps | `feat(f01): validate script & docs` |