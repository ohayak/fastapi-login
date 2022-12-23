from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from models.base_uuid_model import BaseUUIDModel
from models.user_model import User
from uuid import UUID


class CompanyBase(SQLModel):
    name: str
    description: Optional[str]
    address: Optional[str]


class Company(BaseUUIDModel, CompanyBase, table=True):
    created_by_id: Optional[UUID] = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Company.created_by_id==User.id",
        }
    )
    users: List["User"] = Relationship(
        back_populates="company",
        sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "[User.company_id]"},
    )
