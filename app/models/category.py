from datetime import datetime

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, sa_column_kwargs={"nullable": False})
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})