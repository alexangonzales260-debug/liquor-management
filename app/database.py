from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

from app.config import settings
from app.models.product import Product

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


__all__ = ["Product", "SessionLocal", "engine", "init_db"]