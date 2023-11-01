from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, validator

from models.group_model import Group
from models.role_model import Role
from models.user_model import UserBase
from schemas.socialaccount_schema import ISocialAccountCreateWithId, ISocialAccountRead
from schemas.wallet_schema import IWalletCreateWithId, IWalletRead
from utils.partial import optional

from .media_schema import IImageMediaRead
from .role_schema import IRoleRead


class IUserSignup(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class IUserCreate(UserBase):
    password: Optional[str]


# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


class IUserRead(UserBase):
    id: UUID
    role: Optional[str]
    groups: Optional[List[str]]
    image: Optional[IImageMediaRead]
    wallets: Optional[List[IWalletRead]]
    social_accounts: Optional[List[ISocialAccountRead]]
    scopes: Optional[List[str]]
    primary_wallet: Optional[IWalletRead]

    @validator("scopes", pre=True)
    def validate_scopes(cls, value, values) -> List[str]:
        scopes = []
        if role := values.get("role"):
            scopes.expend(role.scopes)

        if groups := values.get("groups"):
            for group in groups:
                scopes.extend(group.scopes)
        return scopes

    @validator("role", pre=True)
    def validate_role(cls, value: Role, values) -> Optional[str]:
        if value:
            return value.name

    @validator("groups", pre=True)
    def validate_groups(cls, value: List[Group], values) -> List[str]:
        if value:
            return [group.name for group in value]
        else:
            return []


class IUserUpsert(UserBase):
    id: UUID
    password: Optional[str]
    role: Optional[str]
    groups: Optional[List[str]]
    wallets: Optional[List[IWalletCreateWithId]]
    social_accounts: Optional[List[ISocialAccountCreateWithId]]
    primary_wallet: Optional[str]


class IUserReadBasic(UserBase):
    id: UUID
    role: Optional[IRoleRead]
    image: Optional[IImageMediaRead]


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
