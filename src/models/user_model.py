from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import ARRAY, VARCHAR, Column, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import LinkGroupUser


class UserBase(SQLModel):
    first_name: str
    last_name: Optional[str]
    email: Optional[EmailStr] = Field(sa_column=Column(VARCHAR, nullable=True, index=True, unique=True))
    email_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    role_id: Optional[UUID] = Field(foreign_key="Role.id")
    phone: Optional[str]
    image_id: Optional[UUID] = Field(foreign_key="ImageMedia.id")


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str]
    social_logins: Optional[List[str]] = Field(sa_column=Column(ARRAY(VARCHAR()), default=[]))
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
    groups: List["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    image: Optional["ImageMedia"] = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "selectin",
        }
    )
