from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from fastapi import Body, Query
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


class FilterQuery(BaseModel):
    filter_by: Optional[str] = None
    min: Union[float, datetime, str, None] = None
    max: Union[float, datetime, str, None] = None
    eq: Union[float, datetime, bool, str, None] = None
    like: str = None
    order_by: Optional[str] = None
    order: Optional[IOrderEnum] = IOrderEnum.ascendent


class AggRequestForm(BaseModel):
    group_by: List[str] = Body(description="compute avg for these columns")
    avg: List[str] = Body([], description="compute avg for these columns")
    sum: List[str] = Body([], description="compute sum for these columns")
    min: List[str] = Body([], description="compute min for these columns")
    max: List[str] = Body([], description="compute max for these columns")
    count: List[str] = Body([], description="compute count for these columns")
