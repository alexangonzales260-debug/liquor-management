from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, select

from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale

router = APIRouter(prefix="/api/sales", tags=["sales"])

Db = Annotated[Session, Depends(get_db)]


class SaleInput(SQLModel):
    product_id: int
    qty: int = Field(gt=0)


@router.get("", response_model=list[Sale])
def list_sales(db: Db) -> list[Sale]:
    statement = select(Sale).order_by(Sale.created_at.desc(), Sale.id.desc())
    return list(db.exec(statement).all())


@router.post("", response_model=Sale, status_code=201)
def register_sale(payload: SaleInput, db: Db) -> Sale:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if payload.qty > product.stock:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    if product.price_cents is None:
        raise HTTPException(status_code=400, detail="Product has no price")
    sale = Sale(
        product_id=product.id,
        qty=payload.qty,
        unit_price_cents=product.price_cents,
        total_cents=payload.qty * product.price_cents,
    )
    product.stock -= payload.qty
    db.add(sale)
    db.add(product)
    db.commit()
    db.refresh(sale)
    return sale