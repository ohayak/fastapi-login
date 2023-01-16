from typing import Any, Dict, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from models.battery_model import BatteryCell, BatteryEvolution, BatteryInfo, BatteryModel, BatteryReview, BatteryState
from schemas.battery_schema import (
    IBatteryCellRead,
    IBatteryEvolutionRead,
    IBatteryInfoRead,
    IBatteryModelRead,
    IBatteryReviewRead,
    IBatteryStateRead,
)


class CRUDBatteryCell(CRUDBase[BatteryCell, Dict[str, Any], IBatteryCellRead]):
    async def get_by_ref(self, *, ref: str, db_session: Optional[AsyncSession]) -> BatteryCell:
        cell = await db_session.execute(select(BatteryCell).where(BatteryCell.cell_ref == ref))
        return cell.scalar_one_or_none()


batcell = CRUDBatteryCell(BatteryCell)


class CRUDBatteryModel(CRUDBase[BatteryModel, Dict[str, Any], IBatteryModelRead]):
    async def get_by_ref(self, *, ref: str, db_session: Optional[AsyncSession]) -> BatteryModel:
        model = await db_session.execute(select(BatteryModel).where(BatteryModel.model_ref == ref))
        return model.scalar_one_or_none()


batmodel = CRUDBatteryModel(BatteryModel)


class CRUDBatteryInfo(CRUDBase[BatteryInfo, Dict[str, Any], IBatteryInfoRead]):
    ...


batinfo = CRUDBatteryInfo(BatteryInfo)


class CRUDBatteryState(CRUDBase[BatteryState, Dict[str, Any], IBatteryStateRead]):
    ...


batstate = CRUDBatteryState(BatteryState)


class CRUDBatteryEvolution(CRUDBase[BatteryEvolution, Dict[str, Any], IBatteryEvolutionRead]):
    ...


batevolution = CRUDBatteryEvolution(BatteryEvolution)


class CRUDBatteryReview(CRUDBase[BatteryReview, Dict[str, Any], IBatteryReviewRead]):
    ...


batreview = CRUDBatteryReview(BatteryReview)
