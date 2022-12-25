from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic.networks import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.security import get_password_hash, verify_password
from crud.base_crud import CRUDBase
from db.asqlalchemy import db
from models.media_model import ImageMedia, Media
from models.user_model import User
from schemas.media_schema import IMediaCreate
from schemas.user_schema import IUserCreate, IUserUpdate


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(self, *, email: str, db_session: Optional[AsyncSession] = None) -> Optional[User]:
        db_session = db_session or db.session
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def create_with_role(self, *, obj_in: IUserCreate, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or db.session
        db_obj = User.from_orm(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update_is_active(
        self, *, db_obj: List[User], obj_in: Union[int, str, Dict[str, Any]]
    ) -> Union[User, None]:
        response = None
        for x in db_obj:
            setattr(x, "is_active", obj_in.is_active)
            setattr(x, "updated_at", datetime.utcnow())
            db.session.add(x)
            await db.session.commit()
            await db.session.refresh(x)
            response.append(x)
        return response

    async def authenticate(self, *, email: EmailStr, password: str) -> Optional[User]:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_photo(
        self,
        *,
        user: User,
        image: IMediaCreate,
        heigth: int,
        width: int,
        file_format: str,
        db_session: Optional[AsyncSession] = None
    ) -> User:
        db_session = db_session or db.session
        user.image = ImageMedia(
            media=Media.from_orm(image),
            height=heigth,
            width=width,
            file_format=file_format,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def remove(self, *, id: Union[UUID, str], db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or db.session
        response = await db_session.execute(select(self.model).where(self.model.id == id))
        obj = response.scalar_one()

        await db_session.delete(obj)
        await db_session.commit()
        return obj


user = CRUDUser(User)
