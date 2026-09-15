from datetime import datetime

from sqlmodel import Field, SQLModel


class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    qty: int = Field(gt=0)
    unit_price_cents: int
    total_cents: int
    created_at: datetime = Field(default_factory=datetime.utcnow)