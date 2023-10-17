from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic.networks import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.security import get_password_hash, verify_password
from crud.base_crud import CRUDBase
from middlewares.asql import get_ctx_session
from models.media_model import ImageMedia, Media
from models.user_model import User
from schemas.media_schema import IMediaCreate
from schemas.user_schema import IUserCreate, IUserUpdate


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(self, *, email: str, db_session: Optional[AsyncSession] = None) -> Optional[User]:
        db_session = db_session or get_ctx_session()
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def create_with_role(
        self, *, obj_in: IUserCreate, role_id: UUID, db_session: Optional[AsyncSession] = None
    ) -> User:
        db_session = db_session or get_ctx_session()
        db_obj = User.from_orm(obj_in)
        if obj_in.password:
            db_obj.hashed_password = get_password_hash(obj_in.password)
        db_obj.role_id = role_id
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def add_social_login(
        self, *, user: User, social_login: str, db_session: Optional[AsyncSession] = None
    ) -> User:
        db_session = db_session or get_ctx_session()
        if social_login not in user.social_logins:
            social_logins = [social_login] if not user.social_logins else set(user.social_logins + [social_login])
            user.social_logins = social_logins
            user.updated_at = datetime.utcnow()
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
        return user

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
        db_session = db_session or get_ctx_session()
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


user = CRUDUser(User)
