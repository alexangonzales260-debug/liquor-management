from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlmodel import Field, Session, SQLModel, col, func, select

from app.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.models.supplier import Supplier

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])

Db = Annotated[Session, Depends(get_db)]


class SupplierCreate(SQLModel):
    name: str = Field(min_length=1)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    notes: str | None = None


class SupplierUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    notes: str | None = None


class SupplierRead(SQLModel):
    id: int
    name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    notes: str | None = None
    created_at: datetime
    order_count: int = 0


def get_supplier_or_404(supplier_id: int, db: Session) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def supplier_name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    statement = select(Supplier).where(func.lower(Supplier.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Supplier.id != exclude_id)
    return db.exec(statement).first() is not None


def orders_count(db: Session, supplier_id: int) -> int:
    return db.exec(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.supplier_id == supplier_id)).one()  # type: ignore[arg-type]


def to_supplier_read(supplier: Supplier, db: Session) -> SupplierRead:
    return SupplierRead(
        id=supplier.id,  # type: ignore[arg-type]
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        tax_id=supplier.tax_id,
        notes=supplier.notes,
        created_at=supplier.created_at,
        order_count=orders_count(db, supplier.id),  # type: ignore[arg-type]
    )


@router.get("", response_model=list[SupplierRead])
def list_suppliers(
    db: Db,
    q: Annotated[str | None, Query()] = None,
    sort: Annotated[str, Query()] = "name",
) -> list[SupplierRead]:
    statement = select(Supplier)
    if q is not None:
        statement = statement.where(
            or_(col(Supplier.name).icontains(q), col(Supplier.contact_person).icontains(q))
        )
    if sort == "created_at":
        statement = statement.order_by(Supplier.created_at.asc(), Supplier.id.asc())  # type: ignore[attr-defined,union-attr]
    else:
        statement = statement.order_by(Supplier.name.asc())  # type: ignore[attr-defined,union-attr]
    suppliers = db.exec(statement).all()
    return [to_supplier_read(supplier, db) for supplier in suppliers]


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: int, db: Db) -> SupplierRead:
    return to_supplier_read(get_supplier_or_404(supplier_id, db), db)


@router.post("", response_model=SupplierRead, status_code=201)
def create_supplier(payload: SupplierCreate, db: Db) -> SupplierRead:
    if supplier_name_exists(db, payload.name):
        raise HTTPException(status_code=422, detail="Supplier name already exists")
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return to_supplier_read(supplier, db)


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: int, payload: SupplierUpdate, db: Db) -> SupplierRead:
    supplier = get_supplier_or_404(supplier_id, db)
    data = payload.model_dump(exclude_unset=True)
    name = data.get("name")
    if name is not None and supplier_name_exists(db, name, exclude_id=supplier.id):
        raise HTTPException(status_code=422, detail="Supplier name already exists")
    for key, value in data.items():
        setattr(supplier, key, value)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return to_supplier_read(supplier, db)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Db) -> None:
    supplier = get_supplier_or_404(supplier_id, db)
    if orders_count(db, supplier.id) > 0:  # type: ignore[arg-type]
        raise HTTPException(status_code=409, detail="Supplier has associated purchase orders")
    db.delete(supplier)
    db.commit()