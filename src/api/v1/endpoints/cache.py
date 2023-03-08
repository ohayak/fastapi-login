from datetime import datetime
from typing import Union

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

import crud
from schemas.response_schema import IGetResponseBase, create_response

router = APIRouter()


@router.get("/cached", response_model=IGetResponseBase[Union[str, datetime]])
@cache(expire=10)
async def get_a_cached_response():
    """
    Gets a cached datetime
    """
    return create_response(data=datetime.now())


@router.get("/no_cached", response_model=IGetResponseBase[Union[str, datetime]])
async def get_a_normal_response():
    """
    Gets a real-time datetime
    """
    return create_response(data=datetime.now())
