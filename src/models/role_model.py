from enum import Enum
from typing import List

from sqlmodel import VARCHAR, Column, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import RoleScopeLink, Scope
from models.user_model import User


class RoleEnum(str, Enum):
    senator = "senator"
    deputy = "deputy"
    citizen = "citizen"


class RoleBase(SQLModel):
    name: RoleEnum = Field(sa_column=Column(VARCHAR, nullable=False, unique=True))
    description: str


class Role(BaseUUIDModel, RoleBase, table=True):
    scopes: List[Scope] = Relationship(link_model=RoleScopeLink, sa_relationship_kwargs={"lazy": "selectin"})
    users: List[User] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "User.role_id"}
    )
