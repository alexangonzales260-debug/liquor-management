from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlmodel import Field, Session, SQLModel, col, func, select

from app.database import get_db
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from app.models.restock import Restock
from app.models.supplier import Supplier

router = APIRouter(prefix="/api/purchase-orders", tags=["purchase-orders"])

Db = Annotated[Session, Depends(get_db)]


class PurchaseOrderCreate(SQLModel):
    supplier_id: int
    product_id: int
    qty_ordered: int = Field(gt=0)
    unit_cost_cents: int = Field(ge=0)
    expected_date: date | None = None
    notes: str | None = None


class PurchaseOrderUpdate(SQLModel):
    supplier_id: int | None = None
    product_id: int | None = None
    qty_ordered: int | None = Field(default=None, gt=0)
    qty_received: int | None = Field(default=None, ge=0)
    unit_cost_cents: int | None = Field(default=None, ge=0)
    status: PurchaseOrderStatus | None = None
    expected_date: date | None = None
    received_date: date | None = None
    notes: str | None = None


class ReceiveRequest(SQLModel):
    qty_received: int = Field(gt=0)


class PurchaseOrderRead(SQLModel):
    id: int
    supplier_id: int
    supplier_name: str
    product_id: int
    product_name: str
    qty_ordered: int
    qty_received: int
    unit_cost_cents: int
    total_cost_cents: int
    status: PurchaseOrderStatus
    order_date: date
    expected_date: date | None = None
    received_date: date | None = None
    notes: str | None = None
    restock_ids: list[int] = Field(default_factory=list)
    created_at: datetime


class ReceiveResult(SQLModel):
    po: PurchaseOrderRead
    restock_id: int


def _supports_for_update(db: Session) -> bool:
    if db.bind is None:
        return False
    return db.bind.dialect.name != "sqlite"


def get_po_or_404(po_id: int, db: Session, for_update: bool = False) -> PurchaseOrder:
    statement = select(PurchaseOrder).where(PurchaseOrder.id == po_id)
    if for_update and _supports_for_update(db):
        statement = statement.with_for_update()
    po = db.exec(statement).one_or_none()
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


def calculate_total_cost(qty: int, unit_cost_cents: int) -> int:
    return qty * unit_cost_cents


def to_po_read(po: PurchaseOrder, db: Session) -> PurchaseOrderRead:
    return PurchaseOrderRead(
        id=po.id,  # type: ignore[arg-type]
        supplier_id=po.supplier_id,
        supplier_name=po.supplier.name,
        product_id=po.product_id,
        product_name=po.product.name,
        qty_ordered=po.qty_ordered,
        qty_received=po.qty_received,
        unit_cost_cents=po.unit_cost_cents,
        total_cost_cents=po.total_cost_cents,
        status=po.status,
        order_date=po.order_date,
        expected_date=po.expected_date,
        received_date=po.received_date,
        notes=po.notes,
        restock_ids=restock_ids_for(db, po.id),
        created_at=po.created_at,
    )


def restock_count(db: Session, po_id: int) -> int:
    return db.exec(select(func.count(Restock.id)).where(Restock.purchase_order_id == po_id)).one()  # type: ignore[arg-type]


def restock_ids_for(db: Session, po_id: int | None) -> list[int]:
    statement = select(Restock).where(Restock.purchase_order_id == po_id)
    return [r.id for r in db.exec(statement).all() if r.id is not None]


@router.get("", response_model=list[PurchaseOrderRead])
def list_purchase_orders(
    db: Db,
    supplier_id: Annotated[int | None, Query()] = None,
    product_id: Annotated[int | None, Query()] = None,
    status: Annotated[PurchaseOrderStatus | None, Query()] = None,
    q: Annotated[str | None, Query()] = None,
) -> list[PurchaseOrderRead]:
    statement = select(PurchaseOrder)
    if supplier_id is not None:
        statement = statement.where(PurchaseOrder.supplier_id == supplier_id)
    if product_id is not None:
        statement = statement.where(PurchaseOrder.product_id == product_id)
    if status is not None:
        statement = statement.where(PurchaseOrder.status == status)
    if q is not None:
        statement = statement.join(Supplier, col(PurchaseOrder.supplier_id) == col(Supplier.id)).join(
            Product, col(PurchaseOrder.product_id) == col(Product.id)
        ).where(
            or_(col(Supplier.name).icontains(q), col(Product.name).icontains(q))
        )
    statement = statement.order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.id.desc())  # type: ignore[attr-defined,union-attr]
    orders = db.exec(statement).all()
    return [to_po_read(order, db) for order in orders]


@router.get("/{po_id}", response_model=PurchaseOrderRead)
def get_purchase_order(po_id: int, db: Db) -> PurchaseOrderRead:
    return to_po_read(get_po_or_404(po_id, db), db)


@router.post("", response_model=PurchaseOrderRead, status_code=201)
def create_purchase_order(payload: PurchaseOrderCreate, db: Db) -> PurchaseOrderRead:
    if db.get(Supplier, payload.supplier_id) is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if db.get(Product, payload.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    order = PurchaseOrder(
        supplier_id=payload.supplier_id,
        product_id=payload.product_id,
        qty_ordered=payload.qty_ordered,
        qty_received=0,
        unit_cost_cents=payload.unit_cost_cents,
        total_cost_cents=calculate_total_cost(payload.qty_ordered, payload.unit_cost_cents),
        expected_date=payload.expected_date,
        notes=payload.notes,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return to_po_read(order, db)


@router.put("/{po_id}", response_model=PurchaseOrderRead)
def update_purchase_order(po_id: int, payload: PurchaseOrderUpdate, db: Db) -> PurchaseOrderRead:
    po = get_po_or_404(po_id, db)
    if po.status != PurchaseOrderStatus.pending:
        raise HTTPException(status_code=409, detail="Only pending purchase orders can be updated")
    data = payload.model_dump(exclude_unset=True)
    new_supplier_id = data.get("supplier_id")
    if (
        new_supplier_id is not None
        and new_supplier_id != po.supplier_id
        and db.get(Supplier, new_supplier_id) is None
    ):
        raise HTTPException(status_code=404, detail="Supplier not found")
    new_product_id = data.get("product_id")
    if (
        new_product_id is not None
        and new_product_id != po.product_id
        and db.get(Product, new_product_id) is None
    ):
        raise HTTPException(status_code=404, detail="Product not found")
    qty_received = data.get("qty_received")
    qty_ordered = data.get("qty_ordered")
    if qty_received is not None and qty_received < po.qty_received:
        raise HTTPException(status_code=400, detail="Cannot reduce qty_received")
    if qty_ordered is not None and qty_ordered < po.qty_received:
        raise HTTPException(status_code=400, detail="qty_ordered cannot be below qty_received")
    received_after = qty_received if qty_received is not None else po.qty_received
    ordered_after = qty_ordered if qty_ordered is not None else po.qty_ordered
    if received_after > ordered_after:
        raise HTTPException(status_code=400, detail="qty_received cannot exceed qty_ordered")
    for key, value in data.items():
        setattr(po, key, value)
    if qty_ordered is not None or data.get("unit_cost_cents") is not None:
        po.total_cost_cents = calculate_total_cost(po.qty_ordered, po.unit_cost_cents)
    db.add(po)
    db.commit()
    db.refresh(po)
    return to_po_read(po, db)


@router.delete("/{po_id}", status_code=204)
def delete_purchase_order(po_id: int, db: Db) -> None:
    po = get_po_or_404(po_id, db)
    if po.status != PurchaseOrderStatus.pending or po.qty_received != 0:
        raise HTTPException(
            status_code=409,
            detail="Only pending purchase orders without received stock can be deleted",
        )
    if restock_count(db, po_id) > 0:
        raise HTTPException(status_code=409, detail="Purchase order has associated restocks")
    db.delete(po)
    db.commit()


@router.post("/{po_id}/receive", response_model=ReceiveResult, status_code=201)
def receive_purchase_order(po_id: int, payload: ReceiveRequest, db: Db) -> ReceiveResult:
    po = get_po_or_404(po_id, db, for_update=True)
    if po.status not in (PurchaseOrderStatus.pending, PurchaseOrderStatus.partial):
        raise HTTPException(
            status_code=409,
            detail="Only pending or partial purchase orders can receive stock",
        )
    qty_new = payload.qty_received
    pending_qty = po.qty_ordered - po.qty_received
    if qty_new > pending_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot receive more than the pending quantity ({pending_qty})",
        )
    product = db.get(Product, po.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    restock = Restock(
        product_id=po.product_id,
        qty=qty_new,
        unit_cost_cents=po.unit_cost_cents,
        total_cost_cents=calculate_total_cost(qty_new, po.unit_cost_cents),
        purchase_order_id=po.id,
    )
    product.stock += qty_new
    po.qty_received += qty_new
    if po.qty_received == po.qty_ordered:
        po.status = PurchaseOrderStatus.received
        po.received_date = date.today()  # noqa: DTZ011
    elif po.qty_received > 0:
        po.status = PurchaseOrderStatus.partial
    db.add(restock)
    db.add(product)
    db.add(po)
    db.commit()
    db.refresh(restock)
    db.refresh(po)
    return ReceiveResult(
        po=to_po_read(po, db),
        restock_id=restock.id,  # type: ignore[arg-type]
    )