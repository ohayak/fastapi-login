import logging
from datetime import datetime
from typing import Any, Dict, Generic, List, Literal, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.sql.expression import ColumnCollection
from sqlmodel import ARRAY, SQLModel, Unicode, and_, func, literal, select, type_coerce
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

from db.asqlalchemy import db
from schemas.common_schema import FilterQuery, GroupQuery, IOrderEnum

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
        query: Optional[Union[T, Select[T]]] = None,
        skip: int = 0,
        limit: int = 100,
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
        query: Optional[Union[T, Select[T]]] = None,
        params: Optional[Params] = Params(),
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session
        if query is None:
            query = select(self.model)
        return await paginate(db_session, query, params)

    async def get_multi_paginated_ordered(
        self,
        *,
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.ascendent,
        params: Optional[Params] = Params(),
        selectexp: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        if order_by is not None:
            if order_by not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"order_by must be a valid column from {columns.keys()}",
                )
            else:
                order_by = columns[order_by]

        if selectexp is None:
            selectexp = select(self.model)

        query = selectexp

        if order_by is not None:
            if order == IOrderEnum.ascendent:
                query = query.order_by(order_by.asc())
            else:
                query = query.order_by(order_by.desc())

        logging.debug(f"Paginate query: {query}")
        return await paginate(db_session, query, params)

    def _select_from_filter(
        self,
        columns: Union[ColumnCollection, Dict],
        query: FilterQuery,
        selectexp: Optional[Union[T, Select[T]]] = None,
        clause: Literal["where", "filter", "having"] = "where",
    ):
        filter_by = query.filter_by
        min = query.min
        max = query.max
        eq = query.eq
        isin = query.isin
        like = query.like
        order_by = query.order_by
        order = query.order

        if selectexp is None:
            query = select(self.model)
        else:
            query = selectexp

        if filter_by is not None:
            if filter_by not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"filter_by must be a valid column from {columns.keys()}",
                )

            conditions = sum(
                [(min is not None) or (max is not None), (eq is not None), (like is not None), (isin is not None)]
            )

            if conditions != 1:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="if filter_by defined exactly one condition is required",
                )

            filter_by = columns[filter_by]

            criteria = ()
            if min and max:
                criteria = and_(min <= filter_by, filter_by <= max)
            elif max:
                criteria = filter_by <= max
            elif min:
                criteria = filter_by >= min
            elif eq:
                criteria = filter_by == eq
            elif like:
                criteria = filter_by.ilike(f"%{like}%")
            elif isin:
                criteria = filter_by.in_(isin)

            if clause == "having":
                query = query.having(criteria)
            elif clause == "filter":
                query = query.filter(criteria)
            else:
                query = query.where(criteria)

        if order_by is not None:
            if order_by not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"order_by must be a valid column from {columns.keys()}",
                )

            order_by = columns[order_by]
            if order == IOrderEnum.ascendent:
                query = query.order_by(order_by.asc())
            else:
                query = query.order_by(order_by.desc())

        return query

    async def get_multi_filtered_paginated_ordered(
        self,
        *,
        filters: FilterQuery = FilterQuery(),
        params: Optional[Params] = Params(),
        selectexp: Optional[Union[T, Select[T]]] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:

        db_session = db_session or db.session
        columns = self.model.__table__.columns

        if filters.filter_by is None:
            return await self.get_multi_paginated_ordered(
                params=params,
                order_by=filters.order_by,
                order=filters.order,
                selectexp=selectexp,
                db_session=db_session,
            )

        query = self._select_from_filter(columns, filters, selectexp)

        logging.debug(f"Paginate query: {query}")
        return await paginate(db_session, query, params)

    async def get_multi_grouped_paginated(
        self,
        *,
        filters: FilterQuery = FilterQuery(),
        groups: GroupQuery = GroupQuery(),
        params: Optional[Params] = Params(),
        db_session: Optional[AsyncSession] = None,
    ) -> Page[ModelType]:
        db_session = db_session or db.session

        columns = self.model.__table__.columns

        group_by = groups.group_by
        avg = groups.avg
        min = groups.min
        max = groups.max
        sum = groups.sum
        count = groups.count
        array = groups.array

        if not group_by:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="group_by can't be empty",
            )

        for c in group_by:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of group_by not a valid value from {columns.keys()}",
                )

        operations = group_by + avg + min + max + sum + count + array

        if len(operations) != len(set(operations)):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="ambigious query each element must apear once",
            )

        filter_cols = {}
        clauses = ()
        for c in group_by:
            filter_cols[c] = columns[c]
            clauses += (columns[c],)

        agg = func.count().label("count")
        filter_cols[agg.name] = agg
        selection = (agg,) + clauses

        for c in avg:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of avg not a valid value from {columns.keys()}",
                )
            agg = func.avg(columns[c]).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)
        for c in min:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of min not a valid value from {columns.keys()}",
                )
            agg = func.min(columns[c]).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)
        for c in max:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of max not a valid value from {columns.keys()}",
                )
            agg = func.max(columns[c]).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)
        for c in count:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of count not a valid value from {columns.keys()}",
                )
            agg = func.count(columns[c]).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)
        for c in sum:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of sum not a valid value from {columns.keys()}",
                )
            agg = func.sum(columns[c]).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)
        for c in array:
            if c not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"element {c} of array not a valid value from {columns.keys()}",
                )
            agg = func.array_agg(columns[c], type_=ARRAY(Unicode, as_tuple=True)).label(c)
            filter_cols[agg.name] = agg
            selection = selection + (agg,)

        query = select(selection).group_by(*clauses)

        query = self._select_from_filter(filter_cols, filters, query, clause="having")

        logging.debug(f"Paginate query: {query}")
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

        if order_by is not None:
            if order_by not in columns:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"order_by must be a valid column from {columns.keys()}",
                )
            else:
                order_by = columns[order_by]

        query = select(self.model).offset(skip).limit(limit)

        if order_by is not None:
            if order == IOrderEnum.ascendent:
                query = query.order_by(order_by.asc())
            else:
                query = query.order_by(order_by.desc())

        logging.debug(f"Exec query: {query}")
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
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
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
