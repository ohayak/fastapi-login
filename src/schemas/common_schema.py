from enum import Enum
from typing import List

from pydantic import BaseModel

from schemas.role_schema import IRoleRead


class IMetaGeneral(BaseModel):
    roles: List[IRoleRead]


class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"
