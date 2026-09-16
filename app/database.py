from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
from app.models.alert_rule import AlertRule
from app.models.category import Category
from app.models.notification import Notification
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.restock import Restock
from app.models.sale import Sale
from app.models.supplier import Supplier

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


__all__ = [
    "AlertRule",
    "Category",
    "Notification",
    "Product",
    "PurchaseOrder",
    "Restock",
    "Sale",
    "SessionLocal",
    "Supplier",
    "engine",
    "get_db",
    "init_db",
]