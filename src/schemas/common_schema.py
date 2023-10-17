from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from fastapi import Body, Query
from pydantic import BaseModel, Field

from .role_schema import IRoleRead
from .user_schema import IUserRead


class IMetaGeneral(BaseModel):
    roles: List[IRoleRead]


class IOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"
    ID = "id_token"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int
    user: IUserRead


class RefreshToken(BaseModel):
    refresh_token: str


class FilterQuery(BaseModel):
    filter_by: Optional[str] = Query(None)
    min: Union[float, datetime, str, None] = Query(None)
    max: Union[float, datetime, str, None] = Query(None)
    eq: Union[float, datetime, bool, str, None] = Query(None)
    neq: Union[float, datetime, bool, str, None] = Query(None)
    nullable: Optional[bool] = Query(
        None, description="if true force include null values, if false force exclude null values"
    )
    like: str = Query(None)
    # Fix for https://github.com/tiangolo/fastapi/issues/4445
    isin: Optional[List[Union[float, datetime, bool, str]]] = Field(Query(None))
    isnotin: Optional[List[Union[float, datetime, bool, str]]] = Field(Query(None))
    order_by: Optional[str] = Query(None)
    order: Optional[IOrderEnum] = Query(IOrderEnum.asc)


class GroupQuery(BaseModel):
    group_by: List[str] = Body([], description="group by keys")
    avg: List[str] = Body([], description="compute avg for these columns")
    sum: List[str] = Body([], description="compute sum for these columns")
    min: List[str] = Body([], description="compute min for these columns")
    max: List[str] = Body([], description="compute max for these columns")
    count: List[str] = Body([], description="compute count for these columns")
    array: List[str] = Body([], description="array aggregation for these columns")
