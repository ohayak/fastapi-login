from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import declared_attr
from sqlmodel import Column, Field, ForeignKey
from sqlmodel import SQLModel as _SQLModel
from sqlmodel.sql.sqltypes import GUID


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseLinkModel(SQLModel):
    updated_at: Optional[datetime] = Field(default=datetime.now())
    created_at: Optional[datetime] = Field(default=datetime.now())


class LinkGroupUser(BaseLinkModel, table=True):
    group_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Group.id", ondelete="cascade"), primary_key=True))
    user_id: str = Field(sa_column=Column(GUID, ForeignKey("User.id", ondelete="cascade"), primary_key=True))
