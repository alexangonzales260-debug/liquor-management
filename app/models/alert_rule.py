from datetime import datetime
from enum import Enum

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    low_stock = "low_stock"
    po_overdue = "po_overdue"
    po_received = "po_received"
    sale_threshold = "sale_threshold"
    restock_created = "restock_created"


class AlertRule(SQLModel, table=True):
    __tablename__ = "alert_rules"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, sa_column_kwargs={"nullable": False})
    event_type: EventType = Field(sa_column_kwargs={"nullable": False})
    condition_json: dict = Field(sa_column_kwargs={"nullable": False}, sa_type=JSON)
    is_active: bool = Field(default=True, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow, "nullable": False},
    )