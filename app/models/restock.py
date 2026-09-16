from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.purchase_order import PurchaseOrder


class Restock(SQLModel, table=True):
    __tablename__ = "restocks"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    qty: int = Field(gt=0)
    unit_cost_cents: int | None = None
    total_cost_cents: int | None = None
    notes: str | None = None
    purchase_order_id: int | None = Field(default=None, foreign_key="purchase_orders.id", nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})

    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="restock")