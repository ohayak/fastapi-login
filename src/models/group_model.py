from enum import Enum
from typing import List

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import LinkGroupUser
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
    users: List["User"] = Relationship(
        back_populates="groups",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
