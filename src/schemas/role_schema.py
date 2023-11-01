from typing import List
from uuid import UUID

from pydantic import validator

from models.role_model import RoleBase
from utils.partial import optional


class IRoleCreate(RoleBase):
    pass


# All these fields are optional
@optional
class IRoleUpdate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID
    scopes: List[str]

    @validator("scopes", pre=True)
    def validate_scopes(cls, value, values) -> List[str]:
        return [scope.name for scope in values["scopes"]]
