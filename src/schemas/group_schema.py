from typing import List, Optional
from models.group_model import GroupBase
from utils.partial import optional
from uuid import UUID
from .user_schema import IUserReadWithoutGroups


class IGroupCreate(GroupBase):
    pass


class IGroupRead(GroupBase):
    id: UUID

# All these fields are optional
@optional
class IGroupUpdate(GroupBase):
    pass


class IGroupReadWithUsers(GroupBase):
    id: UUID
    users: Optional[List[IUserReadWithoutGroups]] = []


