from enum import Enum
from typing import List, Optional
from uuid import UUID

from models.group_model import GroupBase
from models.user_model import UserBase
from utils.partial import optional

from .media_schema import IImageMediaRead
from .role_schema import IRoleRead


class IUserCreate(UserBase):
    password: Optional[str]


# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


# This schema is used to avoid circular import
class IGroupReadBasic(GroupBase):
    id: UUID


class IUserRead(UserBase):
    id: UUID
    role: Optional[IRoleRead]
    groups: Optional[List[IGroupReadBasic]] = []
    image: Optional[IImageMediaRead]


class IUserReadWithoutGroups(UserBase):
    id: UUID
    role: Optional[IRoleRead]
    image: Optional[IImageMediaRead]


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
