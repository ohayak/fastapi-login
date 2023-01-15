from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import exc
from sqlmodel import SQLModel, and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

from db.asqlalchemy import db
from schemas.common_schema import IOrderEnum

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, *, id: Union[UUID, str], db_session: Optional[AsyncSession] = None) -> Optional[ModelType]:
        db_session = db_session or db.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_ids(
        self,
        *,
        list_ids: List[Union[UUID, str]],
        db_session: Optional[AsyncSession] = None,
    ) -> Optional[List[ModelType]]:
        db_session = db_session or db.session
        response = await db_session.execute(select(self.model).where(self.model.id.in_(list_ids)))
        return response.scalars().all()

    async def get_count(self, db_session: Optional[AsyncSession] = None) -> Optional[ModelType]:
        db_session = db_session or db.session
        response = await db_session.execute(select(func.count()).select_from(select(self.model).subquery()))
        return response.scalar_one()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> List[ModelType]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        response = await db_session.execute(query)
        return response.scalars().all()

    async def get_multi_paginated(
        self,
        *,
        params: Optional[Params] = Params(),
        query: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model)
        return await paginate(db_session, query, params)

    async def get_multi_paginated_ordered(
        self,
        *,
        params: Optional[Params] = Params(),
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.ascendent,
        query: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            order_by = self.model.id

        if query is None:
            if order == IOrderEnum.ascendent:
                query = select(self.model).order_by(columns[order_by].asc())
            else:
                query = select(self.model).order_by(columns[order_by].desc())

        return await paginate(db_session, query, params)

    async def get_multi_filtered_paginated_ordered(
        self,
        *,
        filter_by: Optional[str] = None,
        min: Any = None,
        max: Any = None,
        eq: Any = None,
        params: Optional[Params] = Params(),
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.ascendent,
        query: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session

        if filter_by is None:
            return await self.get_multi_paginated_ordered(
                params=params, order_by=order_by, order=order, query=query, db_session=db_session
            )

        columns = self.model.__table__.columns

        if filter_by not in columns:
            raise HTTPException(
                status_code=409,
                detail="filter_by must be a valid value",
            )

        if order_by not in columns or order_by is None:
            order_by = self.model.id

        if query is None:
            criteria = ()
            if min:
                criteria = and_(criteria, columns[filter_by] >= min)
            if max:
                criteria = and_(criteria, columns[filter_by] <= max)
            if eq:
                criteria = columns[filter_by] == eq
            if order == IOrderEnum.ascendent:
                query = select(self.model).where(criteria).order_by(columns[order_by].asc())
            else:
                query = select(self.model).where(criteria).order_by(columns[order_by].desc())

        return await paginate(db_session, query, params)

    async def get_multi_ordered(
        self,
        *,
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.ascendent,
        skip: int = 0,
        limit: int = 100,
        db_session: Optional[AsyncSession] = None,
    ) -> List[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by not in columns or order_by is None:
            order_by = self.model.id

        if order == IOrderEnum.ascendent:
            query = select(self.model).offset(skip).limit(limit).order_by(columns[order_by.value].asc())
        else:
            query = select(self.model).offset(skip).limit(limit).order_by(columns[order_by.value].desc())

        response = await db_session.execute(query)
        return response.scalars().all()

    async def create(
        self,
        *,
        obj_in: Union[CreateSchemaType, ModelType],
        created_by_id: Optional[Union[UUID, str]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> ModelType:
        db_session = db_session or db.session
        db_obj = self.model.from_orm(obj_in)  # type: ignore
        db_obj.created_at = datetime.utcnow()
        db_obj.updated_at = datetime.utcnow()
        if created_by_id:
            db_obj.created_by_id = created_by_id

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: Union[UpdateSchemaType, Dict[str, Any], ModelType],
        db_session: Optional[AsyncSession] = None,
    ) -> ModelType:
        db_session = db_session or db.session
        obj_data = jsonable_encoder(obj_current)

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in obj_data:
            if field in update_data:
                setattr(obj_current, field, update_data[field])
            if field == "updated_at":
                setattr(obj_current, field, datetime.utcnow())

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def remove(self, *, id: Union[UUID, str], db_session: Optional[AsyncSession] = None) -> ModelType:
        db_session = db_session or db.session
        response = await db_session.execute(select(self.model).where(self.model.id == id))
        obj = response.scalar_one()
        await db_session.delete(obj)
        await db_session.commit()
        return obj
