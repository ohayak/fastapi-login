from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from models.base_uuid_model import BaseUUIDModel, SQLModel
from models.user_model import User


class WalletBase(SQLModel):
    chain: str
    name: Optional[str]
    provider: Optional[str]
    public_key: str = Field(unique=True)
    user_id: UUID = Field(foreign_key="User.id")


class Wallet(BaseUUIDModel, WalletBase, table=True):
    user: User = Relationship(
        back_populates="wallets",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "Wallet.user_id",
        },
    )  # noqa: F821
