from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.purchase_order import PurchaseOrder


class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, unique=True, index=True, sa_column_kwargs={"nullable": False})
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})

    orders: list["PurchaseOrder"] = Relationship(back_populates="supplier")