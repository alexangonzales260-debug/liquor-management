from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.restock import Restock
    from app.models.supplier import Supplier


class PurchaseOrderStatus(str, Enum):
    pending = "pending"
    partial = "partial"
    received = "received"
    cancelled = "cancelled"


class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: int | None = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="suppliers.id", ondelete="RESTRICT")
    product_id: int = Field(foreign_key="products.id", ondelete="RESTRICT")
    qty_ordered: int = Field(gt=0)
    qty_received: int = Field(default=0, ge=0)
    unit_cost_cents: int = Field(ge=0)
    total_cost_cents: int
    status: PurchaseOrderStatus = Field(default=PurchaseOrderStatus.pending, index=True)
    order_date: date = Field(default_factory=date.today)
    expected_date: date | None = None
    received_date: date | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})

    supplier: "Supplier" = Relationship(back_populates="orders")
    product: "Product" = Relationship()
    restock: Optional["Restock"] = Relationship(back_populates="purchase_order")

    @model_validator(mode="after")
    def _check_qty_received_le_ordered(self) -> "PurchaseOrder":
        if self.qty_received > self.qty_ordered:
            raise ValueError("qty_received cannot exceed qty_ordered")
        return self