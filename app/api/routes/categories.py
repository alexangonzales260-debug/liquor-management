from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, func, select

from app.database import get_db
from app.models.category import Category
from app.models.product import Product

router = APIRouter(prefix="/api/categories", tags=["categories"])

Db = Annotated[Session, Depends(get_db)]


class CategoryInput(SQLModel):
    name: str = Field(min_length=1)
    description: str | None = None


class CategoryOut(SQLModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    products_count: int = 0


def get_category_or_404(category_id: int, db: Session) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def category_name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    statement = select(Category).where(func.lower(Category.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Category.id != exclude_id)
    return db.exec(statement).first() is not None


def products_count(db: Session, category_name: str) -> int:
    return db.exec(select(func.count(Product.id)).where(Product.category == category_name)).one()  # type: ignore[arg-type]


def to_category_out(category: Category, db: Session) -> CategoryOut:
    return CategoryOut(
        id=category.id,  # type: ignore[arg-type]
        name=category.name,
        description=category.description,
        created_at=category.created_at,
        products_count=products_count(db, category.name),
    )


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Db) -> list[CategoryOut]:
    categories = db.exec(
        select(Category).order_by(Category.name.asc())  # type: ignore[attr-defined,union-attr]
    ).all()
    return [to_category_out(category, db) for category in categories]


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryInput, db: Db) -> CategoryOut:
    if category_name_exists(db, payload.name):
        raise HTTPException(status_code=400, detail="Category already exists")
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return to_category_out(category, db)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Db) -> CategoryOut:
    return to_category_out(get_category_or_404(category_id, db), db)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryInput, db: Db) -> CategoryOut:
    category = get_category_or_404(category_id, db)
    if category_name_exists(db, payload.name, exclude_id=category.id):
        raise HTTPException(status_code=400, detail="Category already exists")
    if payload.name != category.name:
        products = db.exec(select(Product).where(Product.category == category.name)).all()
        for product in products:
            product.category = payload.name
            db.add(product)
    category.name = payload.name
    category.description = payload.description
    db.add(category)
    db.commit()
    db.refresh(category)
    return to_category_out(category, db)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Db) -> None:
    category = get_category_or_404(category_id, db)
    if products_count(db, category.name) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with associated products")
    db.delete(category)
    db.commit()