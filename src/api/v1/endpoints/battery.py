from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi_pagination import Params
from sqlmodel import select

import crud
from api import deps
from core.config import settings
from models.battery_model import BatteryCell, BatteryInfo, BatteryModel
from models.user_model import User
from schemas.battery_schema import (
    IBatteryCellRead,
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
    IPutResponseBase,
    create_response,
)
from utils.exceptions import ContentNoChangeException, IdNotFoundException, NameExistException

router = APIRouter()


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
    "/cell/{cell_id}",
    response_model=IGetResponseBase[IBatteryCellRead],
)
async def get_cell_by_id(
    cell_id: UUID, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a cell by its id
    """
    cell = await crud.batcell.get(id=cell_id, db_session=db)
    if cell:
        return create_response(data=cell)
    else:
        raise IdNotFoundException(BatteryCell, id=cell_id)


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
    "/model/{cell_id}",
    response_model=IGetResponseBase[IBatteryModelRead],
)
async def get_model_by_id(
    model_id: UUID, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a model by its id
    """
    model = await crud.batmodel.get(id=model_id, db_session=db)
    if model:
        return create_response(data=model)
    else:
        raise IdNotFoundException(BatteryModel, id=model_id)


@router.get("/info", response_model=IGetResponsePaginated[IBatteryInfoRead])
async def get_infos(
    params: Params = Depends(), current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of infos
    """
    infos = await crud.batinfo.get_multi_paginated(params=params, db_session=db)
    return create_response(data=infos)


@router.get(
    "/{schema}/evolution/filter",
    response_model=IGetResponsePaginated[IBatteryEvolutionRead],
)
async def get_evolution_filtered(
    schema: str,
    filter_by: str,
    min: Optional[float] = None,
    max: Optional[float] = None,
    eq: Any = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of evolutions filtred by soh
    """
    evolution = await crud.batevolution.get_multi_filtered_paginated_ordered(
        filter_by=filter_by, min=min, max=max, eq=eq, params=params, order_by=order_by, order=order, db_session=db
    )
    return create_response(data=evolution)


@router.get(
    "/{schema}/review/filter",
    response_model=IGetResponsePaginated[IBatteryReviewRead],
)
async def get_review_filtered(
    schema: str,
    filter_by: str,
    min: Optional[float] = None,
    max: Optional[float] = None,
    eq: Any = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of reviews filtred by soh
    """
    review = await crud.batreview.get_multi_filtered_paginated_ordered(
        filter_by=filter_by, min=min, max=max, eq=eq, params=params, order_by=order_by, order=order, db_session=db
    )
    return create_response(data=review)


@router.get(
    "/{schema}/state/filter",
    response_model=IGetResponsePaginated[IBatteryStateRead],
)
async def get_state_filtered(
    schema: str,
    filter_by: str,
    min: Optional[float] = None,
    max: Optional[float] = None,
    eq: Any = None,
    order_by: str = "id",
    order: IOrderEnum = IOrderEnum.ascendent,
    current_user: User = Depends(deps.get_current_user()),
    params: Params = Depends(),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of states filtred by soh
    """
    state = await crud.batstate.get_multi_filtered_paginated_ordered(
        filter_by=filter_by, min=min, max=max, eq=eq, params=params, order_by=order_by, order=order, db_session=db
    )
    return create_response(data=state)
