from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import VARCHAR, Column, DateTime, Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.links_model import GroupUserLink


class UserBase(SQLModel):
    email: Optional[EmailStr] = Field(sa_column=Column(VARCHAR, nullable=True, index=True, unique=True))
    email_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_new: bool = Field(default=True)
    role_id: Optional[UUID] = Field(foreign_key="Role.id")
    country: Optional[str]
    email_notification: Optional[bool]
    discord_notification: Optional[bool]
    newsletter_notification: Optional[bool]
    username: Optional[str] = Field(unique=True)
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    image_id: Optional[UUID] = Field(foreign_key="ImageMedia.id")
    first_visit: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now()))
    last_visit: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=datetime.now()))
    policies_consent: Optional[bool]
    primary_wallet_id: Optional[UUID] = Field(foreign_key="Wallet.id")


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str]
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
    image: Optional["ImageMedia"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})  # noqa: F821
    groups: List["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=GroupUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    wallets: List["Wallet"] = Relationship(  # noqa: F821
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "Wallet.user_id",
        },
    )
    primary_wallet: Optional["Wallet"] = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "User.primary_wallet_id",
        },
    )
    social_accounts: List["SocialAccount"] = Relationship(  # noqa: F821
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "SocialAccount.user_id",
        },
    )
