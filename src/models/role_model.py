from typing import List

from sqlmodel import Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel


class RoleBase(SQLModel):
    name: str
    description: str


class Role(BaseUUIDModel, RoleBase, table=True):
    users: List["User"] = Relationship(  # noqa: F821
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "[User.role_id]"}
    )
