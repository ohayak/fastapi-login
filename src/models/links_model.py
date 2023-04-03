from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseLinkModel(SQLModel):
    updated_at: Optional[datetime] = Field(default=datetime.now())
    created_at: Optional[datetime] = Field(default=datetime.now())


class LinkGroupUser(BaseLinkModel, table=True):
    group_id: UUID = Field(foreign_key="Group.id", primary_key=True)
    user_id: UUID = Field(foreign_key="User.id", primary_key=True)
