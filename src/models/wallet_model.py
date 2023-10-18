from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, Relationship
from models.base_uuid_model import SQLModel
from models.user_model import User


class WalletBase(SQLModel):
    name: str = Field(primary_key=True)
    address: str = Field(unique=True)
    user_id: UUID = Field(primary_key=True, foreign_key="User.id")


class Wallet(WalletBase, table=True):
    updated_at: Optional[datetime] = Field(default=datetime.now())
    created_at: Optional[datetime] = Field(default=datetime.now())
    user: User = Relationship(  # noqa: F821
        back_populates="wallets",
        sa_relationship_kwargs={ "lazy": "selectin" }
    )
