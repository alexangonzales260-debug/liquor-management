from datetime import datetime
from enum import Enum

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class Channel(str, Enum):
    email = "email"
    telegram = "telegram"
    webhook = "webhook"
    in_app = "in_app"


class NotificationStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    suppressed = "suppressed"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: int | None = Field(default=None, primary_key=True)
    alert_rule_id: int | None = Field(default=None, foreign_key="alert_rules.id", nullable=True)
    channel: Channel = Field(sa_column_kwargs={"nullable": False})
    recipient: str = Field(sa_column_kwargs={"nullable": False})
    subject: str | None = None
    message: str = Field(sa_column_kwargs={"nullable": False})
    status: NotificationStatus = Field(default=NotificationStatus.pending, sa_column_kwargs={"nullable": False})
    retry_count: int = Field(default=0, sa_column_kwargs={"nullable": False})
    last_attempt_at: datetime | None = None
    sent_at: datetime | None = None
    error_message: str | None = None
    payload_json: dict = Field(sa_column_kwargs={"nullable": False}, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})