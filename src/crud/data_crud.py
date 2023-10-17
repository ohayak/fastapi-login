from typing import List, Optional, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from middlewares.asql import get_ctx_session
from models.data_model import Country
from schemas.data_schema import ICountryRead

DataModelType = TypeVar("DataModelType", bound=SQLModel)
DataSchemaType = TypeVar("DataSchemaType", bound=BaseModel)


class CRUDData(CRUDBase[DataModelType, DataSchemaType, DataSchemaType]):
    async def get_by_code(
        self,
        code: str,
        *,
        db_session: Optional[AsyncSession] = None,
    ) -> DataModelType:
        db_session = db_session or get_ctx_session()
        query = select(self.model).where(self.model.code == code)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_all(
        self,
        *,
        db_session: Optional[AsyncSession] = None,
    ) -> List[DataModelType]:
        db_session = db_session or get_ctx_session()
        response = await db_session.execute(select(self.model))
        return response.scalars().all()


country = CRUDData[Country, ICountryRead](Country)
