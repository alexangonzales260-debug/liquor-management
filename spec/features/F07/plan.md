# F07 Plan — Alertas / Notificaciones

## Stack y Restricciones
- **Stack**: FastAPI + SQLModel + SQLite + HTML/JS vanilla.
- **Puerta única**: `./validate.sh` (ruff + mypy + pytest + boot check).
- **Sin deps nuevas** si es posible:
  - Email: `aiosmtplib` (nueva dep, necesaria para async email).
  - Telegram/Webhook: `httpx` (ya en deps).
  - Scheduler: `asyncio` loop nativo (sin APScheduler).
  - In-App: Endpoint + vista existentes.

## Estructura de Archivos

### Nuevos archivos a crear
```
app/
├── models/
│   ├── alert_rule.py
│   └── notification.py
├── services/
│   ├── alert_engine.py      # Motor de evaluación de reglas
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── email.py         # aiosmtplib
│   │   ├── telegram.py      # httpx
│   │   ├── webhook.py       # httpx
│   │   └── in_app.py        # BD
│   └── scheduler.py         # asyncio loop
├── api/routes/
│   └── alerts.py
├── static/
│   ├── app.js               # + alert rules + notifications views
│   └── style.css            # + alert styles
├── tests/
│   ├── test_alert_rules.py
│   ├── test_notifications.py
│   └── test_alert_engine.py
└── config.py                # + Settings para canales
```

### Archivos a modificar
- `app/database.py` → importar modelos + `__all__`
- `app/config.py` → Settings para SMTP, Telegram, Webhook
- `app/main.py` → registrar router alerts + arrancar scheduler en lifespan
- `app/static/app.js` → vistas `#/alerts` + `#/notifications`
- `app/static/index.html` → sidebar links + vistas
- `app/static/style.css` → estilos alertas/notificaciones
- `app/tests/conftest.py` → fixture para tests de alertas
- `README.md` → documentación endpoints + vistas

## Fases del Plan

### Fase 1 — Modelos y Base de Datos (T1)
**Archivos**: `app/models/alert_rule.py`, `app/models/notification.py`, `app/database.py`
**Objetivo**: Modelos SQLModel + migración via `create_all`.
**Verificación**: `init_db()` crea tablas `alert_rules`, `notifications`; mypy/ruff/pytest OK.

### Fase 2 — API AlertRules (T2)
**Archivos**: `app/api/routes/alerts.py` (rules endpoints), `app/main.py`
**Objetivo**: CRUD `/api/alerts/rules` + validación `condition_json` schema.
**Verificación**: Tests 201/422/404/200/204; mypy/ruff/pytest OK.

### Fase 3 — API Notifications + Motor de Eventos + Test Channel (T3)
**Archivos**: `app/api/routes/alerts.py` (notifications), `app/services/alert_engine.py`, `app/services/channels/`, `app/services/channels/email.py`, `telegram.py`, `webhook.py`, `in_app.py`, `app/tests/test_alert_rules.py`, `test_notifications.py`
**Objetivo**: CRUD notificaciones + motor que evalúa reglas y dispara canales + endpoint test.
**Verificación**: Test channel envía notificación real; pytest OK.

### Fase 4 — Scheduler + Event Hooks (T4)
**Archivos**: `app/services/scheduler.py`, `app/services/alert_engine.py` (hooks), `app/main.py` (lifespan), `app/api/routes/restocks.py`, `purchase_orders.py`, `sales.py` (event hooks).
**Objetivo**: Asyncio loop (5 min) + hooks en eventos existentes (low_stock, po_overdue, po_received, sale_threshold, restock_created).
**Verificación**: Job low_stock/po_overdue disparan notificaciones; `validate.sh` OK.

### Fase 5 — Frontend: Reglas de Alerta (T5)
**Archivos**: `app/static/index.html`, `app/static/app.js`, `app/static/style.css`, `app/tests/test_frontend.py`
**Objetivo**: Vista `#/alerts` con CRUD reglas + botón "Probar".
**Verificación**: Tests frontend; `validate.sh` OK.

### Fase 6 — Frontend: Historial Notificaciones (T6)
**Archivos**: `app/static/app.js`, `app/static/index.html`, `app/static/style.css`, `app/tests/test_frontend.py`
**Objetivo**: Vista `#/notifications` con filtros, retry, read.
**Verificación**: Tests frontend; `validate.sh` OK.

### Fase 7 — E2E + Docs + Validate (T7)
**Archivos**: `app/tests/test_frontend.py` (E2E), `README.md`, `validate.sh` (ya existe).
**Objetivo**: Test E2E flujo completo (regla low_stock → job → notificación → frontend), actualizar README, `validate.sh` verde.
**Verificación**: `./validate.sh` ALL CHECKS PASSED.

## Orden de Commits (1 tarea = 1 commit)
1. `feat(f07): alert models & db init`
2. `feat(f07): alert rules CRUD API`
3. `feat(f07): notifications API + event engine + channels`
4. `feat(f07): scheduler + event hooks`
5. `feat(f07): alert rules frontend`
6. `feat(f07): notifications frontend`
7. `feat(f07): e2e tests, docs & validate`

## Verificación Continua
Cada tarea debe dejar `./validate.sh` en verde (ruff + mypy + pytest + boot).