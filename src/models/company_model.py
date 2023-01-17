from enum import Enum
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from models.base_uuid_model import BaseUUIDModel
from models.user_model import User


class CompanyStatusEnum(str, Enum):
    OPERATOR = "OPERATOR"
    REPAIRER = "REPAIRER"
    RECYCLER = "RECYCLER"
    SECONDLIFE = "SECONDLIFE"


class CompanyBase(SQLModel):
    name: str
    description: Optional[str]
    address: Optional[str]
    status: Optional[CompanyStatusEnum]
    repair_partner: Optional[str]


class Company(BaseUUIDModel, CompanyBase, table=True):
    created_by_id: Optional[UUID] = Field(foreign_key="User.id")
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Company.created_by_id==User.id",
        }
    )
    contact_id: Optional[UUID] = Field(foreign_key="User.id")
    contact: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Company.contact_id==User.id",
        }
    )
    users: List["User"] = Relationship(
        back_populates="company",
        sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "[User.company_id]"},
    )
