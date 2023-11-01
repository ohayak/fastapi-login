from enum import Enum
from typing import List

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import GroupScopeLink, GroupUserLink, Scope
from models.user_model import User


class GroupEnum(str, Enum):
    admin = "admin"
    player = "player"
    gm = "gm"
    npc = "npc"
    bot = "bot"


class GroupBase(SQLModel):
    name: GroupEnum = Field(sa_column=Column(VARCHAR, nullable=False, unique=True))
    description: str


class Group(BaseUUIDModel, GroupBase, table=True):
    scopes: List[Scope] = Relationship(link_model=GroupScopeLink, sa_relationship_kwargs={"lazy": "selectin"})
    users: List[User] = Relationship(
        back_populates="groups", link_model=GroupUserLink, sa_relationship_kwargs={"lazy": "selectin"}
    )
