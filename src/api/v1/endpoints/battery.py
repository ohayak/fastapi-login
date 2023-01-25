from typing import Dict

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi_pagination import Params
from sqlmodel import select

import crud.battery_crud as crud
from api import deps
from models.battery_model import BatteryCell, BatteryInfo, BatteryModel
from models.user_model import User
from schemas.battery_schema import (
    IBatteryCellRead,
    IBatteryCompanyDataRead,
    IBatteryEvolutionRead,
    IBatteryInfoRead,
    IBatteryModelRead,
    IBatteryReviewRead,
    IBatteryStateInfoRead,
    IBatteryStateRead,
)
from schemas.common_schema import FilterQuery, GroupQuery, IOrderEnum
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
    query: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a paginated list of infos
    """
    infos = await crud.batinfo.get_multi_filtered_paginated(
        filters=query,
        params=params,
        db_session=db,
    )
    return create_response(data=infos, meta={"quey": query})


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
    query: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of evolutions
    """
    evolution = await crud.batevolution.get_multi_filtered_paginated(
        filters=query,
        params=params,
        db_session=db,
    )
    return create_response(data=evolution, meta={"quey": query})


@router.get(
    "/{schema}/review",
    response_model=IGetResponsePaginated[IBatteryReviewRead],
)
async def get_review_filtered(
    schema: str,
    query: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of reviews
    """
    review = await crud.batreview.get_multi_filtered_paginated(
        filters=query,
        params=params,
        db_session=db,
    )
    return create_response(data=review, meta={"quey": query})


@router.get(
    "/{schema}/state",
    response_model=IGetResponsePaginated[IBatteryStateRead],
)
async def get_state_filtered(
    schema: str,
    query: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of states
    """
    state = await crud.batstate.get_multi_filtered_paginated(
        filters=query,
        params=params,
        db_session=db,
    )
    return create_response(data=state, meta={"quey": query})


@router.get(
    "/{schema}/state/info",
    response_model=IGetResponsePaginated[IBatteryStateInfoRead],
)
async def get_state_info_filtered(
    schema: str,
    query: FilterQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of states
    """
    state = await crud.batstate.get_state_info(
        filters=query,
        params=params,
        db_session=db,
    )
    return create_response(data=state, meta={"quey": query})


@router.post(
    "/{schema}/evolution/agg",
    response_description="Aggregation operation results depends on query",
    response_model=IPostResponsePaginated[Dict],
)
async def post_evolution_agg(
    schema: str,
    query: FilterQuery = Depends(),
    body: GroupQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of evolutions
    """
    evolution = await crud.batevolution.get_multi_grouped_paginated(
        filters=query,
        groups=body,
        params=params,
        db_session=db,
    )
    return create_response(data=evolution, meta={"quey": query, "body": body})


@router.post(
    "/{schema}/review/agg",
    response_description="Aggregation operation results depends on query",
    response_model=IPostResponsePaginated[Dict],
)
async def post_review_agg(
    schema: str,
    query: FilterQuery = Depends(),
    body: GroupQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of reviews
    """
    review = await crud.batreview.get_multi_grouped_paginated(
        filters=query,
        groups=body,
        params=params,
        db_session=db,
    )
    return create_response(data=review, meta={"quey": query, "body": body})


@router.post(
    "/{schema}/state/agg",
    response_description="Aggregation operation results depends on query",
    response_model=IPostResponsePaginated[Dict],
)
async def post_state_agg(
    schema: str,
    query: FilterQuery = Depends(),
    body: GroupQuery = Depends(),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
    db=Depends(deps.get_db_by_schema),
):
    """
    Gets a filtred paginated list of state
    """
    state = await crud.batstate.get_multi_grouped_paginated(
        filters=query,
        groups=body,
        params=params,
        db_session=db,
    )
    return create_response(data=state, meta={"quey": query, "body": body})
