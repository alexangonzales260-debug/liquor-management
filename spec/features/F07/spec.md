# F07 Specification — Alertas / Notificaciones

## Contexto y Objetivo
Añadir un sistema de alertas y notificaciones multi-canal al gestor de licores para avisar de eventos críticos (stock bajo, órdenes de compra vencidas/recepcionadas, ventas por encima de umbral, reposiciones) a través de Email, Telegram, Webhook y notificaciones In-App.

## Modelo de Datos

### `AlertRule` (tabla `alert_rules`)
| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int | PK autoincremental |
| `name` | str | Único, índice, requerido, no vacío |
| `event_type` | Enum | `low_stock`, `po_overdue`, `po_received`, `sale_threshold`, `restock_created` |
| `condition_json` | JSON | Umbrales/condiciones (ej. `{"stock_lt": 5}`, `{"days_overdue": 3}`) |
| `is_active` | bool | Default `true` |
| `created_at` | datetime | Default UTC |
| `updated_at` | datetime | Default UTC, onupdate UTC |

### `Notification` (tabla `notifications`)
| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int | PK |
| `alert_rule_id` | int | FK → `alert_rules.id`, nullable |
| `channel` | Enum | `email`, `telegram`, `webhook`, `in_app` |
| `recipient` | str | Email, chat_id, URL webhook, etc. |
| `subject` | str | Asunto (para email) |
| `message` | str | Cuerpo del mensaje |
| `status` | Enum | `pending`, `sent`, `failed`, `suppressed` |
| `retry_count` | int | Default 0 |
| `last_attempt_at` | datetime | Nullable |
| `sent_at` | datetime | Nullable |
| `error_message` | str | Nullable |
| `payload_json` | JSON | Snapshot del evento que disparó |
| `created_at` | datetime | Default UTC |

## Configuración de Canales (en `app/config.py` vía variables de entorno)
- **Email**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_TLS`, `SMTP_FROM`, `SMTP_FROM_NAME`
- **Telegram**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- **Webhook**: `WEBHOOK_URL`, `WEBHOOK_HEADERS` (JSON), `WEBHOOK_TIMEOUT`, `WEBHOOK_RETRIES`
- **In-App**: No requiere config externa

## Eventos Disparadores

| Evento | Origen | Datos disponibles en `payload_json` |
|---|---|---|
| `low_stock` | Job periódico / `POST /api/restocks` / `POST /api/sales` | `product_id`, `stock_actual`, `threshold` |
| `po_overdue` | Job periódico (cada hora) | `po_id`, `days_overdue`, `supplier_name`, `product_name` |
| `po_received` | `POST /api/purchase-orders/{id}/receive` | `po_id`, `qty_received`, `status` |
| `sale_threshold` | `POST /api/sales` | `product_id`, `qty`, `total_cents` |
| `restock_created` | `POST /api/restocks` | `restock_id`, `qty`, `unit_cost_cents` |

## API REST (`/api/alerts`)

### Reglas (`/api/alerts/rules`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/alerts/rules` | Lista con filtros `event_type`, `is_active` |
| POST | `/api/alerts/rules` | Crea regla (valida `condition_json` schema) |
| GET | `/api/alerts/rules/{id}` | Detalle |
| PUT | `/api/alerts/rules/{id}` | Actualiza (incluye toggle `is_active`) |
| DELETE | `/api/alerts/rules/{id}` | Elimina (204) |

### Notificaciones (`/api/alerts/notifications`)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/alerts/notifications` | Lista con filtros `channel`, `status`, `alert_rule_id`, rango fechas |
| GET | `/api/alerts/notifications/{id}` | Detalle |
| PUT | `/api/alerts/notifications/{id}/read` | Marca leída (solo `in_app`) |
| POST | `/api/alerts/test` | Dispara notificación de prueba (body: `channel`, `recipient`, `subject?`, `message?`) |

## Frontend (hash-routing)
- **Sidebar**: Enlaces `#/alerts` (Reglas) y `#/notifications` (Historial).
- **`#/alerts`**: CRUD reglas + botón "Probar" (dispara test a canal configurado).
- **`#/notifications`**: Lista con filtros (`channel`, `status`, `alert_rule_id`, rango fechas), badges estado, botón "Reintentar" para `failed`, "Marcar leída" (`in_app`).

## Job Programador (Background)
- **Implementación**: `asyncio` loop simple (sin APScheduler, sin dep extra).
- **Frecuencia**: Configurable (default 5 min, variable `ALERT_CHECK_INTERVAL_MINUTES`).
- **Checks**:
  - `low_stock`: Query productos con `stock <= threshold` (desde `AlertRule.condition_json`).
  - `po_overdue`: POs con `status IN (pending, partial)` y `expected_date < today`.

## Criterios de Aceptación
1. CRUD `/api/alerts/rules` funciona; validación `condition_json` schema.
2. CRUD `/api/alerts/notifications` + `PUT /read` funciona.
3. `POST /api/alerts/test` dispara notificación real en canal configurado.
4. Job `low_stock` dispara notificación cuando stock <= umbral.
5. Job `po_overdue` dispara notificación por POs vencidos.
6. Recepción de PO dispara notificación `po_received`.
6. Frontend `#/alerts` y `#/notifications` funcional con filtros, retry, read.
7. `./validate.sh` verde (ruff + mypy + pytest + boot).

## Fuera de Alcance
- Plantillas de mensaje con Jinja2 (usar f-strings simples en MVP).
- Digest diario/semanal.
- Suscripciones de usuario múltiples (MVP: un recipient por regla).
- APScheduler / Celery / Redis (usamos asyncio loop simple).

## Decisiones Clave
- **aiosmtplib** para Email (async, sin bloquear event loop).
- **httpx** para Telegram y Webhook (ya en deps).
- **asyncio loop** para scheduler (sin APScheduler, sin dep extra).
- **Pydantic v2** para validación de `condition_json` schemas.
- **In-App** notificaciones persistidas en BD + endpoint dedicado.