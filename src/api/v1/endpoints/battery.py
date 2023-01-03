from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params
from sqlmodel import select

import crud
from api import deps
from models.battery_model import BatteryCell, BatteryEvolution, BatteryInfo, BatteryModel, BatteryReview, BatteryState
from models.user_model import User
from schemas.battery_schema import (
    IBatteryCellRead,
    IBatteryEvolutionRead,
    IBatteryInfoRead,
    IBatteryModelRead,
    IBatteryReviewRead,
    IBatteryStateRead,
)
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
        params: Params = Depends(), current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of cells
    """
    cells = await crud.batcell.get_multi_paginated(params=params, db_session=db)
    return create_response(data=cells)


@router.get(
    "/cell/{cell_id}",
    response_model=IGetResponseBase[IBatteryCellRead],
    status_code=status.HTTP_200_OK,
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
        params: Params = Depends(), current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of models
    """
    models = await crud.batmodel.get_multi_paginated(params=params, db_session=db)
    return create_response(data=models)


@router.get(
    "/model/{cell_id}",
    response_model=IGetResponseBase[IBatteryModelRead],
    status_code=status.HTTP_200_OK,
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
        params: Params = Depends(), current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema)
):
    """
    Gets a paginated list of infos
    """
    infos = await crud.batinfo.get_multi_paginated(params=params, db_session=db)
    return create_response(data=infos)


@router.get(
    "/info/{info_id}",
    response_model=IGetResponseBase[IBatteryInfoRead],
    status_code=status.HTTP_200_OK,
)
async def get_info_by_id(
        info_id: UUID, current_user: User = Depends(deps.get_current_user()), db=Depends(deps.get_db_by_schema)
):
    """
    Gets a model by its id
    """
    info = await crud.batinfo.get(id=info_id, db_session=db)
    if info:
        return create_response(data=info)
    else:
        raise IdNotFoundException(BatteryInfo, id=info_id)


@router.get("/review/{schema}", response_model=IGetResponsePaginated[IBatteryReviewRead])
async def get_reviews(
        schema: str,
        params: Params = Depends(),
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a paginated list of reviews
    """
    reviews = await crud.batreview.get_multi_paginated(params=params, db_session=db)
    return create_response(data=reviews)


@router.get(
    "/review/{schema}/{review_id}",
    response_model=IGetResponseBase[IBatteryReviewRead],
    status_code=status.HTTP_200_OK,
)
async def get_review_by_id(
        review_id: UUID,
        schema: str,
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a review by its id
    """
    review = await crud.batreview.get(id=review_id, db_session=db)
    if review:
        return create_response(data=review)
    else:
        raise IdNotFoundException(BatteryReview, id=review_id)


@router.get("/state/{schema}", response_model=IGetResponsePaginated[IBatteryStateRead])
async def get_states(
        schema: str,
        params: Params = Depends(),
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a paginated list of states
    """
    states = await crud.batmodel.get_multi_paginated(params=params, db_session=db)
    return create_response(data=states)


@router.get(
    "/state/{schema}/{state_id}",
    response_model=IGetResponseBase[IBatteryStateRead],
    status_code=status.HTTP_200_OK,
)
async def get_state_by_id(
        state_id: UUID,
        schema: str,
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a state by its id
    """
    state = await crud.batstate.get(id=state_id, db_session=db)
    if state:
        return create_response(data=state)
    else:
        raise IdNotFoundException(BatteryState, id=state_id)


@router.get("/evolution/{schema}", response_model=IGetResponsePaginated[IBatteryEvolutionRead])
async def get_evolutions(
        schema: str,
        params: Params = Depends(),
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a paginated list of evolutions
    """
    evolustions = await crud.batmodel.get_multi_paginated(params=params, db_session=db)
    return create_response(data=evolustions)


@router.get(
    "/evolution/{schema}/{evolution_id}",
    response_model=IGetResponseBase[IBatteryEvolutionRead],
    status_code=status.HTTP_200_OK,
)
async def get_evolution_by_id(
        evolution_id: UUID,
        schema: str,
        current_user: User = Depends(deps.get_current_user()),
        db=Depends(deps.get_db_by_schema),
):
    """
    Gets a evolution by its id
    """
    evolution = await crud.batevolution.get(id=evolution_id, db_session=db)
    if evolution:
        return create_response(data=evolution)
    else:
        raise IdNotFoundException(BatteryEvolution, id=evolution_id)


@router.get("/filter_with_soh/{soh_min}/{soh_max}",
            response_model=IGetResponsePaginated[IBatteryEvolutionRead])
async def filter_by_soh(soh_min: float, soh_max: float,
                        current_user: User = Depends(deps.get_current_user()),
                        params: Params = Depends(),
                        db=Depends(deps.get_db_by_schema)):
    """
        Gets a paginated list of evolutions filtred by soh
        """
    query = select(BatteryReview).where(BatteryReview.soh > soh_min).where(BatteryReview.soh < soh_max)
    users = await crud.batreview.get_multi_paginated(params=params, query=query)
    return create_response(data=users)
