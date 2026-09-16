# F07 Tasks — Alertas / Notificaciones

## T1 — Modelos AlertRule + Notification + DB init
- **Objetivo**: Crear modelos SQLModel `AlertRule` y `Notification`, registrar en `app/database.py` para `create_all`.
- **Archivos**:
  - `app/models/alert_rule.py`: `AlertRule` (id, name único, event_type enum, condition_json, is_active, created_at, updated_at).
  - `app/models/notification.py`: `Notification` (id, alert_rule_id FK nullable, channel enum, recipient, subject, message, status enum, retry_count, last_attempt_at, sent_at, error_message, payload_json, created_at).
  - `app/database.py`: imports + `__all__` actualizado.
- **Verificar**:
  - `.venv/bin/python -c "from app.database import init_db; init_db()"` → tablas creadas.
  - `.venv/bin/ruff check app` → clean.
  - `.venv/bin/mypy app` → clean.
  - `.venv/bin/pytest app/tests -q` → 135 passed.
- **Commit**: `feat(f07): alert models & db init`

## T2 — API AlertRules CRUD
- **Objetivo**: Router `/api/alerts/rules` con CRUD completo + validación `condition_json`.
- **Archivos**:
  - `app/api/routes/alerts.py`: router + schemas (`AlertRuleCreate`, `AlertRuleUpdate`, `AlertRuleRead`), helpers (`get_rule_or_404`, `rule_name_exists`), endpoints (GET list con filtros, GET by id, POST 201, PUT 200, DELETE 204).
  - `app/main.py`: registrar `alerts_router`.
- **Verificar**:
  - `.venv/bin/ruff check .` → clean.
  - `.venv/bin/mypy app` → clean.
  - `.venv/bin/pytest app/tests -v` → tests `test_alert_rules.py` pasan (crear, duplicado 422, listar, obtener, actualizar, eliminar, filtros).
  - `./validate.sh` → verde.
- **Commit**: `feat(f07): alert rules CRUD API`

## T3 — API Notifications + Motor de Eventos + Canales + Test Channel
- **Objetivo**: CRUD notificaciones + motor de evaluación + canales (email, telegram, webhook, in_app) + endpoint test.
- **Archivos**:
  - `app/api/routes/alerts.py` (extendido): CRUD `/api/alerts/notifications` + `PUT /{id}/read` + `POST /test`.
  - `app/services/alert_engine.py`: `evaluate_rules(event_type, payload)` → busca reglas activas matching, crea `Notification` pendiente, dispara canales.
  - `app/services/channels/__init__.py`: interfaz `Channel` + factory.
  - `app/services/channels/email.py`: `EmailChannel.send(notification)` con `aiosmtplib`.
  - `app/services/channels/telegram.py`: `TelegramChannel.send(notification)` con `httpx`.
  - `app/services/channels/webhook.py`: `WebhookChannel.send(notification)` con `httpx`.
  - `app/services/channels/in_app.py`: `InAppChannel.send(notification)` → inserta en BD.
  - `app/services/alert_engine.py`: `evaluate_rules(event_type, payload)` → busca reglas activas, match `condition_json`, crea notificación, dispara canales.
  - `app/tests/test_alert_rules.py`, `test_notifications.py`, `test_alert_engine.py`.
- **Verificar**:
  - `.venv/bin/ruff check .` → clean.
  - `.venv/bin/mypy app` → clean.
  - `.venv/bin/pytest app/tests -v` → tests pasan (incluye test que dispara canal test real).
  - `./validate.sh` → verde.
- **Commit**: `feat(f07): notifications API + event engine + channels`

## T4 — Scheduler + Event Hooks
- **Objetivo**: Asyncio loop (5 min) para `low_stock` y `po_overdue` + hooks en eventos existentes.
- **Archivos**:
  - `app/services/scheduler.py`: `AlertScheduler` con `asyncio.create_task` loop (intervalo configurable `ALERT_CHECK_INTERVAL_MINUTES`, default 5), métodos `check_low_stock()`, `check_po_overdue()`, `start()`, `stop()`.
  - `app/services/alert_engine.py`: funciones `trigger_low_stock(product)`, `trigger_po_overdue(po)`, `trigger_po_received(po)`, `trigger_sale_threshold(sale)`, `trigger_restock_created(restock)` → llaman `evaluate_rules`.
  - `app/main.py`: `lifespan` inicia `scheduler.start()` y `scheduler.stop()`.
  - `app/api/routes/restocks.py`: en `register_restock` → `trigger_restock_created(restock)`.
  - `app/api/routes/purchase_orders.py`: en `receive_purchase_order` → `trigger_po_received(po)`.
  - `app/api/routes/sales.py`: en `register_sale` → `trigger_sale_threshold(sale)`.
  - `app/services/scheduler.py`: `check_low_stock()` → query productos con stock bajo threshold desde reglas; `check_po_overdue()` → POs pending/partial con `expected_date < today`.
- **Verificar**:
  - `.venv/bin/ruff check .` → clean.
  - `.venv/bin/mypy app` → clean.
  - `.venv/bin/pytest app/tests -v` → tests scheduler + hooks pasan (job low_stock/po_overdue disparan notificaciones).
  - `./validate.sh` → verde.
- **Commit**: `feat(f07): scheduler + event hooks`

## T5 — Frontend: Reglas de Alerta
- **Objetivo**: Vista `#/alerts` con CRUD reglas + botón "Probar".
- **Archivos**:
  - `app/static/index.html`: sidebar link `#/alerts`, vista `#view-alerts` con tabla `#alert-rules-table` + formulario modal `#alert-rule-form` (name, event_type select, condition_json textarea, is_active checkbox, botones Guardar/Cancelar/Probar).
  - `app/static/app.js`: `"alerts"` en `VIEWS`, `loadAlertRules()`, `renderAlertRulesTable()`, `handleAlertRuleSubmit()`, `handleAlertRuleAction()` (editar/eliminar/probar), `loadAlertRuleForTest()`.
  - `app/static/style.css`: estilos tabla, formulario, badges estado.
  - `app/tests/test_frontend.py`: tests de navegación, elementos vista, headers tabla, botón Probar.
- **Verificar**:
  - `node --check app/static/app.js` → OK.
  - `ruff check .` → clean.
  - `mypy app` → clean.
  - `pytest app/tests -v` → tests frontend pasan.
  - `./validate.sh` → verde.
- **Commit**: `feat(f07): alert rules frontend`

## T6 — Frontend: Historial Notificaciones
- **Objetivo**: Vista `#/notifications` con filtros, retry, read.
- **Archivos**:
  - `app/static/index.html`: link `#/notifications` en sidebar, vista `#view-notifications` con filtros (canal, estado, regla, rango fecha), tabla `#notifications-table` (ID, Regla, Canal, Destinatario, Asunto, Estado, Fecha, Acciones), botones "Reintentar" (failed), "Marcar leída" (in_app).
  - `app/static/app.js`: `"notifications"` en `VIEWS`, `loadNotifications(filters)`, `renderNotificationsTable()`, `handleNotificationRetry()`, `handleNotificationRead()`.
  - `app/static/style.css`: estilos tabla notificaciones, badges estado, botones acción.
  - `app/tests/test_frontend.py`: tests navegación, elementos vista, headers tabla, filtros, botones retry/read.
- **Verificar**:
  - `node --check app/static/app.js` → OK.
  - `ruff check .` → clean.
  - `mypy app` → clean.
  - `pytest app/tests -v` → tests frontend pasan.
  - `./validate.sh` → verde.
- **Commit**: `feat(f07): notifications frontend`

## T7 — E2E Tests + Docs + Validate Final
- **Objetivo**: Test E2E flujo completo + actualizar README + validate final.
- **Archivos**:
  - `app/tests/test_frontend.py`: `test_e2e_low_stock_alert_flow` (crea regla low_stock → crea producto stock 3 → job low_stock → notificación creada → frontend muestra en #/notifications), `test_e2e_po_overdue_alert_flow`.
  - `README.md`: documentación endpoints `/api/alerts/rules`, `/api/alerts/notifications`, `/api/alerts/test`, vistas `#/alerts` y `#/notifications`, configuración canales (variables de entorno), scheduler.
  - `validate.sh`: ya existe, solo confirmar que pasa.
- **Verificar**:
  - `./validate.sh` → ALL CHECKS PASSED (ruff + mypy + pytest 135+ + boot).
  - `git describe --tags` → F07 (tras cierre).
- **Commit**: `feat(f07): e2e tests, docs & validate`

## Cierre Feature
- `chore(f07): close feature F07 (docs)` + tag `F07` + push.