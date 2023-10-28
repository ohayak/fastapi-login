from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Column, Field, ForeignKey
from sqlmodel.sql.sqltypes import GUID

from models.base_uuid_model import SQLModel


class BaseLinkModel(SQLModel):
    updated_at: Optional[datetime] = Field(default=datetime.now())
    created_at: Optional[datetime] = Field(default=datetime.now())


class LinkGroupUser(BaseLinkModel, table=True):
    group_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Group.id", ondelete="cascade"), primary_key=True))
    user_id: UUID = Field(sa_column=Column(GUID, ForeignKey("User.id", ondelete="cascade"), primary_key=True))
