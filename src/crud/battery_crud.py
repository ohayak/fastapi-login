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
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryCell:
        cell = await db_session.execute(select(BatteryCell).where(BatteryCell.name == name))
        return cell.scalar_one_or_none()


batcell = CRUDBatteryCell(BatteryCell)


class CRUDBatteryModel(CRUDBase[BatteryModel, Dict[str, Any], IBatteryModelRead]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryModel:
        model = await db_session.execute(select(BatteryModel).where(BatteryModel.name == name))
        return model.scalar_one_or_none()


batmodel = CRUDBatteryModel(BatteryModel)


class CRUDBatteryInfo(CRUDBase[BatteryInfo, Dict[str, Any], IBatteryInfoRead]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryInfo:
        cell = await db_session.execute(select(BatteryInfo).where(BatteryInfo.name == name))
        return cell.scalar_one_or_none()


batinfo = CRUDBatteryInfo(BatteryInfo)


class CRUDBatteryState(CRUDBase[BatteryState, Dict[str, Any], IBatteryStateRead]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryState:
        cell = await db_session.execute(select(BatteryState).where(BatteryState.name == name))
        return cell.scalar_one_or_none()


batstate = CRUDBatteryState(BatteryState)


class CRUDBatteryEvolution(CRUDBase[BatteryEvolution, Dict[str, Any], IBatteryEvolutionRead]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryEvolution:
        model = await db_session.execute(select(BatteryEvolution).where(BatteryEvolution.name == name))
        return model.scalar_one_or_none()


batevolution = CRUDBatteryEvolution(BatteryEvolution)


class CRUDBatteryReview(CRUDBase[BatteryReview, Dict[str, Any], IBatteryReviewRead]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> BatteryReview:
        cell = await db_session.execute(select(BatteryReview).where(BatteryReview.name == name))
        return cell.scalar_one_or_none()


batreview = CRUDBatteryReview(BatteryReview)
