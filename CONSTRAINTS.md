# CONSTRAINTS — Constitución del proyecto
- Stack: FastAPI + SQLite + HTML/JS vanilla. Sin ORMs pesados innecesarios; SQLAlchemy o sqlmodel permitido si se justifica.
- Una tarea = un commit. No editar migraciones ya aplicadas.
- validate.sh es la única puerta: lint + typecheck + tests + build en verde.
- Sin secretos en repo. Sin dependencias nuevas sin aprobación.
- Frontend simple, sin framework SPA para F01.
