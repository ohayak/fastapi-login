from datetime import datetime
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime
from models.links_model import LinkGroupUser
from models.media_model import ImageMedia
from typing import List, Optional
from pydantic import EmailStr
from models.base_uuid_model import BaseUUIDModel
from uuid import UUID


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(
        nullable=True, index=True, sa_column_kwargs={"unique": True}
    )
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    birthdate: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    role_id: Optional[UUID] = Field(default=None, foreign_key="Role.id")
    phone: Optional[str]
    state: Optional[str]
    country: Optional[str]
    address: Optional[str]


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str] = Field(nullable=False, index=True)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
    groups: List["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    image_id: Optional[UUID] = Field(default=None, foreign_key="ImageMedia.id")
    image: Optional[ImageMedia] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "User.image_id==ImageMedia.id",
        }
    )
