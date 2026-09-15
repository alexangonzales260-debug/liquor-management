from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.config import settings
from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale

router = APIRouter(prefix="/api/stats", tags=["stats"])

Db = Annotated[Session, Depends(get_db)]


@router.get("/dashboard")
def dashboard(db: Db) -> dict:
    total_products = db.exec(select(func.count(Product.id))).one()  # type: ignore[arg-type]
    total_sales = db.exec(select(func.count(Sale.id))).one()  # type: ignore[arg-type]
    total_revenue_cents = db.exec(
        select(func.coalesce(func.sum(Sale.total_cents), 0))
    ).one()
    low_stock_rows = db.exec(
        select(Product)
        .where(Product.stock <= settings.STOCK_LOW_THRESHOLD)
        .order_by(Product.stock.asc(), Product.id.asc())  # type: ignore[attr-defined,union-attr]
    ).all()
    low_stock = [{"id": p.id, "name": p.name, "stock": p.stock} for p in low_stock_rows]
    return {
        "total_products": total_products,
        "total_sales": total_sales,
        "total_revenue_cents": total_revenue_cents,
        "low_stock": low_stock,
    }