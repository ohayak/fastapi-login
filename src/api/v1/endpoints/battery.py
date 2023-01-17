from datetime import datetime
from typing import Dict, Optional, Union

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi_pagination import Params
from sqlmodel import select

import crud
from api import deps
from core.config import settings
from models.battery_model import BatteryCell, BatteryInfo, BatteryModel
from models.user_model import User
from schemas.agg_schema import AggRequestForm
from schemas.battery_schema import (
    IBatteryCellRead,
    IBatteryCompanyDataRead,
    IBatteryEvolutionRead,
    IBatteryInfoRead,
    IBatteryModelRead,
    IBatteryReviewRead,
    IBatteryStateRead,
)
from schemas.common_schema import IOrderEnum
from schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPostResponsePaginated,
    IPutResponseBase,
    create_response,
)
from utils.exceptions import ContentNoChangeException, IdNotFoundException, NameExistException

router = APIRouter()


@router.get("/company/{name}", response_model=IGetResponseBase[IBatteryCompanyDataRead])
async def get_company(
    name: str, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of cells
    """
    company = await crud.batcompany.get_by_name(name=name, db_session=db)
    return create_response(data=company)


@router.get("/cell", response_model=IGetResponsePaginated[IBatteryCellRead])
async def get_cells(
    params: Params = Depends(), current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of cells
    """
    cells = await crud.batcell.get_multi_paginated(params=params, db_session=db)
    return create_response(data=cells)


@router.get(
    "/cell/{cell_ref}",
    response_model=IGetResponseBase[IBatteryCellRead],
)
async def get_cell_by_ref(
    cell_ref: str, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a cell by its id
    """
    cell = await crud.batcell.get_by_ref(ref=cell_ref, db_session=db)
    if cell:
        return create_response(data=cell)
    else:
        raise IdNotFoundException(BatteryCell, id=cell_ref)


@router.get("/model", response_model=IGetResponsePaginated[IBatteryModelRead])
async def get_models(
    params: Params = Depends(), current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of models
    """
    models = await crud.batmodel.get_multi_paginated(params=params, db_session=db)
    return create_response(data=models)


@router.get(
    "/model/{model_ref}",
    response_model=IGetResponseBase[IBatteryModelRead],
)
async def get_model_by_ref(
    model_ref: str, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a model by its id
    """
    model = await crud.batmodel.get_by_ref(ref=model_ref, db_session=db)
    if model:
        return create_response(data=model)
    else:
        raise IdNotFoundException(BatteryModel, id=model_ref)


@router.get("/info", response_model=IGetResponsePaginated[IBatteryInfoRead])
async def get_infos_filtred(
    filter_by: Optional[str] = None,
    min: Union[float, datetime, str, None] = None,
    max: Union[float, datetime, str, None] = None,
    eq: Union[bool, float, datetime, str, None] = None,
    like: str = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a paginated list of infos
    """
    infos = await crud.batinfo.get_multi_filtered_paginated_ordered(
        filter_by=filter_by,
        min=min,
        max=max,
        eq=eq,
        like=like,
        params=params,
        order_by=order_by,
        order=order,
        db_session=db,
    )
    return create_response(data=infos)


@router.get(
    "/info/{battery_ref}",
    response_model=IGetResponseBase[IBatteryInfoRead],
)
async def get_info_by_ref(
    battery_ref: str, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a info by its id
    """
    info = await crud.batinfo.get_by_ref(ref=battery_ref, db_session=db)
    if info:
        return create_response(data=info)
    else:
        raise IdNotFoundException(BatteryInfo, id=battery_ref)


@router.get(
    "/{schema}/evolution",
    response_model=IGetResponsePaginated[IBatteryEvolutionRead],
)
async def get_evolution_filtered(
    schema: str,
    filter_by: Optional[str] = None,
    min: Union[float, datetime, str, None] = None,
    max: Union[float, datetime, str, None] = None,
    eq: Union[bool, float, datetime, str, None] = None,
    like: str = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of evolutions
    """
    evolution = await crud.batevolution.get_multi_filtered_paginated_ordered(
        filter_by=filter_by,
        min=min,
        max=max,
        eq=eq,
        like=like,
        params=params,
        order_by=order_by,
        order=order,
        db_session=db,
    )
    return create_response(data=evolution)


@router.get(
    "/{schema}/review",
    response_model=IGetResponsePaginated[IBatteryReviewRead],
)
async def get_review_filtered(
    schema: str,
    filter_by: Optional[str] = None,
    min: Union[float, datetime, str, None] = None,
    max: Union[float, datetime, str, None] = None,
    eq: Union[bool, float, datetime, str, None] = None,
    like: str = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of reviews
    """
    review = await crud.batreview.get_multi_filtered_paginated_ordered(
        filter_by=filter_by,
        min=min,
        max=max,
        eq=eq,
        like=like,
        params=params,
        order_by=order_by,
        order=order,
        db_session=db,
    )
    return create_response(data=review)


@router.get(
    "/{schema}/state",
    response_model=IGetResponsePaginated[IBatteryStateRead],
)
async def get_state_filtered(
    schema: str,
    filter_by: Optional[str] = None,
    min: Union[float, datetime, str, None] = None,
    max: Union[float, datetime, str, None] = None,
    eq: Union[bool, float, datetime, str, None] = None,
    like: str = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of states
    """
    state = await crud.batstate.get_multi_filtered_paginated_ordered(
        filter_by=filter_by,
        min=min,
        max=max,
        eq=eq,
        like=like,
        params=params,
        order_by=order_by,
        order=order,
        db_session=db,
    )
    return create_response(data=state)


@router.post(
    "/{schema}/evolution/agg",
    response_model=IPostResponsePaginated[Dict],
)
async def post_evolution_agg(
    schema: str,
    payload: AggRequestForm,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of evolutions
    """
    evolution = await crud.batevolution.get_multi_grouped_paginated(
        group_by=payload.group_by,
        avg=payload.avg,
        min=payload.min,
        max=payload.max,
        sum=payload.sum,
        count=payload.count,
        params=params,
        db_session=db,
    )
    return create_response(meta=payload, data=evolution)


@router.post(
    "/{schema}/review/agg",
    response_model=IPostResponsePaginated[Dict],
)
async def post_review_agg(
    schema: str,
    payload: AggRequestForm,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of reviews
    """
    review = await crud.batreview.get_multi_grouped_paginated(
        group_by=payload.group_by,
        avg=payload.avg,
        min=payload.min,
        max=payload.max,
        sum=payload.sum,
        count=payload.count,
        params=params,
        db_session=db,
    )
    return create_response(meta=payload, data=review)


@router.post(
    "/{schema}/state/agg",
    response_model=IPostResponsePaginated[Dict],
)
async def post_state_agg(
    schema: str,
    payload: AggRequestForm,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of state
    """
    state = await crud.batstate.get_multi_grouped_paginated(
        group_by=payload.group_by,
        avg=payload.avg,
        min=payload.min,
        max=payload.max,
        sum=payload.sum,
        count=payload.count,
        params=params,
        db_session=db,
    )
    return create_response(meta=payload, data=state)
