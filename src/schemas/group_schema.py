from typing import List
from uuid import UUID

from pydantic import validator

from models.group_model import GroupBase
from utils.partial import optional


class IGroupCreate(GroupBase):
    pass


class IGroupRead(GroupBase):
    id: UUID
    scopes: List[str]

    @validator("scopes", pre=True)
    def validate_scopes(cls, value, values) -> List[str]:
        return [scope.name for scope in values["scopes"]]


# All fields are optional
@optional
class IGroupUpdate(GroupBase):
    pass
