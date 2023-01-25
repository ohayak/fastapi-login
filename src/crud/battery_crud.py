from typing import Any, Dict, Optional

from fastapi import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from models.battery_model import (
    BatteryCell,
    BatteryCompany,
    BatteryEvolution,
    BatteryInfo,
    BatteryModel,
    BatteryReview,
    BatteryState,
    CompanyData,
)
from schemas.common_schema import FilterQuery


class CRUDBatteryCell(CRUDBase[BatteryCell, Dict[str, Any], Dict[str, Any]]):
    async def get_by_ref(self, *, ref: str, db_session: Optional[AsyncSession]) -> BatteryCell:
        cell = await db_session.execute(select(BatteryCell).where(BatteryCell.cell_ref == ref))
        return cell.scalar_one_or_none()


batcell = CRUDBatteryCell(BatteryCell)


class CRUDBatteryModel(CRUDBase[BatteryModel, Dict[str, Any], Dict[str, Any]]):
    async def get_by_ref(self, *, ref: str, db_session: Optional[AsyncSession]) -> BatteryModel:
        model = await db_session.execute(select(BatteryModel).where(BatteryModel.model_ref == ref))
        return model.scalar_one_or_none()


batmodel = CRUDBatteryModel(BatteryModel)


class CRUDBatteryInfo(CRUDBase[BatteryInfo, Dict[str, Any], Dict[str, Any]]):
    async def get_by_ref(self, *, ref: str, db_session: Optional[AsyncSession]) -> BatteryInfo:
        model = await db_session.execute(select(BatteryInfo).where(BatteryInfo.battery_ref == ref))
        return model.scalar_one_or_none()


batinfo = CRUDBatteryInfo(BatteryInfo)


class CRUDBatteryState(CRUDBase[BatteryState, Dict[str, Any], Dict[str, Any]]):
    async def get_state_info(
        self,
        *,
        filters: FilterQuery = FilterQuery(),
        params: Optional[Params] = Params(),
        db_session: Optional[AsyncSession] = None,
    ) -> Dict:
        statecols = BatteryState.__table__.columns.values()
        infocols = [BatteryInfo.warranty_date, BatteryInfo.start_date, BatteryInfo.model_ref, BatteryInfo.external_ref]
        selectexp = select(statecols + infocols).join(
            BatteryInfo, BatteryState.battery_ref == BatteryInfo.battery_ref, isouter=True
        )

        return await self.get_multi_filtered_paginated(
            filters=filters,
            params=params,
            selectexp=selectexp,
            db_session=db_session,
        )


batstate = CRUDBatteryState(BatteryState)


class CRUDBatteryEvolution(CRUDBase[BatteryEvolution, Dict[str, Any], Dict[str, Any]]):
    ...


batevolution = CRUDBatteryEvolution(BatteryEvolution)


class CRUDBatteryReview(CRUDBase[BatteryReview, Dict[str, Any], Dict[str, Any]]):
    ...


batreview = CRUDBatteryReview(BatteryReview)


class CRUDBatteryCompany(CRUDBase[BatteryCompany, Dict[str, Any], Dict[str, Any]]):
    async def get_by_name(self, *, name: str, db_session: Optional[AsyncSession]) -> Dict:
        query = (
            select(BatteryCompany, CompanyData)
            .where(BatteryCompany.name == name)
            .join(CompanyData, BatteryCompany.id == CompanyData.company_id, isouter=True)
        )
        company = await db_session.execute(query)
        company, data = company.one_or_none()
        if data:
            return company.__dict__ | data.__dict__
        else:
            return company.__dict__


batcompany = CRUDBatteryCompany(BatteryCompany)
