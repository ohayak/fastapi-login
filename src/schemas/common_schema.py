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
    filter_by: Optional[str] = Query(None)
    min: Union[float, datetime, str, None] = Query(None)
    max: Union[float, datetime, str, None] = Query(None)
    eq: Union[float, datetime, bool, str, None] = Query(None)
    like: str = Query(None)
    order_by: Optional[str] = Query(None)
    order: Optional[IOrderEnum] = Query(IOrderEnum.ascendent)
    # isin not working as expected
    # See https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#query-parameter-list-multiple-values
    isin: Optional[List[Union[float, datetime, bool, str, None]]] = Query(None, include_in_schema=False)


class GroupQuery(BaseModel):
    group_by: List[str] = Body([], description="group by keys")
    avg: List[str] = Body([], description="compute avg for these columns")
    sum: List[str] = Body([], description="compute sum for these columns")
    min: List[str] = Body([], description="compute min for these columns")
    max: List[str] = Body([], description="compute max for these columns")
    count: List[str] = Body([], description="compute count for these columns")
    array: List[str] = Body([], description="array aggregation for these columns")
