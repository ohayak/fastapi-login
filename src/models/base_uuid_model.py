from datetime import datetime
from typing import Optional

from sqlalchemy.orm import declared_attr
from sqlmodel import Column, DateTime, Field
from sqlmodel import SQLModel as _SQLModel
from uuid6 import UUID, uuid7

# id: implements proposal uuid7 draft4


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now()))
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now()))
