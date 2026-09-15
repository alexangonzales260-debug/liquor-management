from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, col, select

from app.database import SessionLocal
from app.models.product import Product

router = APIRouter(prefix="/api/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Db = Annotated[Session, Depends(get_db)]


class ProductInput(SQLModel):
    name: str
    category: str | None = None
    volume_ml: int | None = Field(default=None, ge=0)
    price_cents: int | None = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)


def get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list[Product])
def list_products(
    db: Db,
    category: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> list[Product]:
    statement = select(Product)
    if category is not None:
        statement = statement.where(Product.category == category)
    if search is not None:
        statement = statement.where(col(Product.name).icontains(search))
    return list(db.exec(statement).all())


@router.post("", response_model=Product, status_code=201)
def create_product(payload: ProductInput, db: Db) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Db) -> Product:
    return get_product_or_404(product_id, db)


@router.put("/{product_id}", response_model=Product)
def replace_product(
    product_id: int, payload: ProductInput, db: Db
) -> Product:
    product = get_product_or_404(product_id, db)
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Db) -> None:
    product = get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()
