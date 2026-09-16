from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, func, select

from app.database import get_db
from app.models.alert_rule import AlertRule, EventType

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

Db = Annotated[Session, Depends(get_db)]


class AlertRuleCreate(SQLModel):
    name: str = Field(min_length=1)
    event_type: EventType
    condition_json: dict
    is_active: bool = True


class AlertRuleUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1)
    event_type: EventType | None = None
    condition_json: dict | None = None
    is_active: bool | None = None


class AlertRuleRead(SQLModel):
    id: int
    name: str
    event_type: EventType
    condition_json: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


def get_rule_or_404(rule_id: int, db: Session) -> AlertRule:
    rule = db.get(AlertRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


def rule_name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    statement = select(AlertRule).where(func.lower(AlertRule.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(AlertRule.id != exclude_id)
    return db.exec(statement).first() is not None


def to_alert_rule_read(rule: AlertRule) -> AlertRuleRead:
    return AlertRuleRead(
        id=rule.id,
        name=rule.name,
        event_type=rule.event_type,
        condition_json=rule.condition_json,
        is_active=rule.is_active,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.get("/rules", response_model=list[AlertRuleRead])
def list_alert_rules(
    db: Db,
    event_type: Annotated[EventType | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
) -> list[AlertRuleRead]:
    statement = select(AlertRule)
    if event_type is not None:
        statement = statement.where(AlertRule.event_type == event_type)
    if is_active is not None:
        statement = statement.where(AlertRule.is_active == is_active)
    statement = statement.order_by(AlertRule.name.asc())  # type: ignore[attr-defined]
    rules = db.exec(statement).all()
    return [to_alert_rule_read(rule) for rule in rules]


@router.get("/rules/{rule_id}", response_model=AlertRuleRead)
def get_alert_rule(rule_id: int, db: Db) -> AlertRuleRead:
    return to_alert_rule_read(get_rule_or_404(rule_id, db))


@router.post("/rules", response_model=AlertRuleRead, status_code=201)
def create_alert_rule(payload: AlertRuleCreate, db: Db) -> AlertRuleRead:
    if rule_name_exists(db, payload.name):
        raise HTTPException(status_code=422, detail="Alert rule name already exists")
    rule = AlertRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return to_alert_rule_read(rule)


@router.put("/rules/{rule_id}", response_model=AlertRuleRead)
def update_alert_rule(rule_id: int, payload: AlertRuleUpdate, db: Db) -> AlertRuleRead:
    rule = get_rule_or_404(rule_id, db)
    data = payload.model_dump(exclude_unset=True)
    name = data.get("name")
    if name is not None and rule_name_exists(db, name, exclude_id=rule.id):
        raise HTTPException(status_code=422, detail="Alert rule name already exists")
    for key, value in data.items():
        setattr(rule, key, value)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return to_alert_rule_read(rule)


@router.delete("/rules/{rule_id}", status_code=204)
def delete_alert_rule(rule_id: int, db: Db) -> None:
    rule = get_rule_or_404(rule_id, db)
    db.delete(rule)
    db.commit()