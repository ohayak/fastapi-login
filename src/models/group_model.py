from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.user_model import User

from .links_model import LinkGroupUser


class GroupBase(SQLModel):
    name: str
    description: str


class Group(BaseUUIDModel, GroupBase, table=True):
    created_by_id: Optional[UUID] = Field(foreign_key="User.id")
    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Group.created_by_id==User.id",
        }
    )
    users: List["User"] = Relationship(
        back_populates="groups",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
