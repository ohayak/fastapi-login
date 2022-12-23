from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import BigInteger, Column, DateTime, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import LinkGroupUser
from models.media_model import ImageMedia


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(nullable=True, index=True, sa_column_kwargs={"unique": True})
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    birthdate: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    role_id: Optional[UUID] = Field(foreign_key="Role.id")
    phone: Optional[str]
    state: Optional[str]
    country: Optional[str]
    address: Optional[str]
    image_id: Optional[UUID] = Field(foreign_key="ImageMedia.id")
    job_title: Optional[str]
    company_id: Optional[UUID] = Field(foreign_key="Company.id")


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
    image: Optional[ImageMedia] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "User.image_id==ImageMedia.id",
        }
    )
    company: Optional["Company"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"lazy": "selectin", "primaryjoin": "User.company_id==Company.id"},
    )
