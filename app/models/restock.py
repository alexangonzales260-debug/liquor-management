from datetime import datetime

from sqlmodel import Field, SQLModel


class Restock(SQLModel, table=True):
    __tablename__ = "restocks"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    qty: int = Field(gt=0)
    unit_cost_cents: int | None = None
    total_cost_cents: int | None = None
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})