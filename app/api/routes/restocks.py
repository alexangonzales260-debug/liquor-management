from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, select

from app.database import get_db
from app.models.product import Product
from app.models.restock import Restock

router = APIRouter(prefix="/api/restocks", tags=["restocks"])

Db = Annotated[Session, Depends(get_db)]


class RestockInput(SQLModel):
    product_id: int
    qty: int = Field(gt=0)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    notes: str | None = None


@router.get("", response_model=list[Restock])
def list_restocks(db: Db) -> list[Restock]:
    statement = select(Restock).order_by(Restock.created_at.desc(), Restock.id.desc())  # type: ignore[attr-defined,union-attr]
    return list(db.exec(statement).all())


@router.post("", response_model=Restock, status_code=201)
def register_restock(payload: RestockInput, db: Db) -> Restock:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    total_cost_cents = (
        payload.qty * payload.unit_cost_cents if payload.unit_cost_cents is not None else None
    )
    restock = Restock(
        product_id=product.id,
        qty=payload.qty,
        unit_cost_cents=payload.unit_cost_cents,
        total_cost_cents=total_cost_cents,
        notes=payload.notes,
    )
    product.stock += payload.qty
    db.add(restock)
    db.add(product)
    db.commit()
    db.refresh(restock)
    return restock