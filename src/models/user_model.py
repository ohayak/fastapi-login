from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import ARRAY, VARCHAR, Column, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import LinkGroupUser
from models.media_model import ImageMedia


class UserBase(SQLModel):
    first_name: str
    last_name: Optional[str]
    email: EmailStr = Field(index=True, sa_column_kwargs={"unique": True})
    is_new: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    role_id: Optional[UUID] = Field(foreign_key="Role.id")
    phone: Optional[str]
    image_id: Optional[UUID] = Field(foreign_key="ImageMedia.id")


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str]
    social_logins: Optional[List[str]] = Field(sa_column=Column(ARRAY(VARCHAR())))
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
    groups: List["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    image: Optional[ImageMedia] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "User.image_id==ImageMedia.id",
        }
    )
    wallets: List["Wallet"] = Relationship(  # noqa: F821
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "User.id==Wallet.user_id",
        },
    )
