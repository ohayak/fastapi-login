from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Column, Field, ForeignKey
from sqlmodel.sql.sqltypes import GUID

from models.base_uuid_model import BaseUUIDModel, SQLModel


class Scope(BaseUUIDModel, table=True):
    name: str = Field(max_length=64, unique=True)


class GroupUserLink(SQLModel, table=True):
    group_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Group.id", ondelete="cascade"), primary_key=True))
    user_id: UUID = Field(sa_column=Column(GUID, ForeignKey("User.id", ondelete="cascade"), primary_key=True))
    created_at: Optional[datetime] = Field(default=datetime.now())


class GroupScopeLink(SQLModel, table=True):
    group_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Group.id", ondelete="cascade"), primary_key=True))
    scope_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Scope.id", ondelete="cascade"), primary_key=True))
    created_at: Optional[datetime] = Field(default=datetime.now())


class RoleScopeLink(SQLModel, table=True):
    role_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Role.id", ondelete="cascade"), primary_key=True))
    scope_id: UUID = Field(sa_column=Column(GUID, ForeignKey("Scope.id", ondelete="cascade"), primary_key=True))
    created_at: Optional[datetime] = Field(default=datetime.now())
