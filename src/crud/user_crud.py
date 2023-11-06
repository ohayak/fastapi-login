from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic.networks import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.security import get_password_hash, verify_password
from crud.base_crud import CRUDBase
from exceptions.common_exception import IdNotFoundException
from middlewares.asql import get_ctx_session
from models.links_model import GroupUserLink
from models.media_model import ImageMedia, Media
from models.socialaccount_model import SocialAccount
from models.user_model import User
from models.wallet_model import Wallet
from schemas.media_schema import IMediaCreate
from schemas.user_schema import IUserCreate, IUserUpdate


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def create(self, *, obj_in: IUserCreate, db_session: Optional[AsyncSession] = None) -> User:
        db_obj = self.model.from_orm(obj_in)
        if obj_in.password:
            db_obj.hashed_password = get_password_hash(obj_in.password)
        user = await super().create(db_obj, db_session)
        return user

    async def remove_from_all_groups(self, user: User, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or get_ctx_session()
        response = await db_session.execute(select(GroupUserLink).where(GroupUserLink.user_id == user.id))
        for obj in response.scalars().all():
            await db_session.delete(obj)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    async def add_to_group(self, user: User, group_id: UUID, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or get_ctx_session()
        for group in user.groups:
            if group.id == group_id:
                return user
        db_session.add(GroupUserLink(group_id=group_id, user_id=user.id))
        await db_session.flush()
        await db_session.refresh(user)
        return user

    async def remove_from_group(self, user: User, group_id: UUID, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or get_ctx_session()
        db_session.delete(GroupUserLink(group_id=group_id, user_id=user.id))
        await db_session.flush()
        await db_session.refresh(user)
        return user

    async def attach_role(self, user: User, role_id: UUID, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or get_ctx_session()
        user.role_id = role_id
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    async def unlink_wallet(self, user: User, wallet_id: UUID, db_session: Optional[AsyncSession] = None) -> User:
        db_session = db_session or get_ctx_session()
        for wallet in user.wallets:
            if wallet.id == wallet_id:
                await db_session.delete(wallet)
                await db_session.flush()
                await db_session.refresh(user)
                return user
        raise IdNotFoundException(Wallet, wallet_id)

    async def unlink_socialaccount(
        self, user: User, account_id: UUID, db_session: Optional[AsyncSession] = None
    ) -> User:
        db_session = db_session or get_ctx_session()
        for account in user.social_accounts:
            if account.id == account_id:
                await db_session.delete(account)
                await db_session.flush()
                await db_session.refresh(user)
                return user
        raise IdNotFoundException(SocialAccount, account_id)

    async def add_social_login(
        self, *, user: User, social_login: str, db_session: Optional[AsyncSession] = None
    ) -> User:
        db_session = db_session or get_ctx_session()
        if social_login not in user.social_logins:
            social_logins = [social_login] if not user.social_logins else set(user.social_logins + [social_login])
            user.social_logins = social_logins
            user.updated_at = datetime.utcnow()
            db_session.add(user)
            await db_session.flush()
            await db_session.refresh(user)
        return user

    async def authenticate(self, *, email: EmailStr, password: str) -> Optional[User]:
        user = await self.get_by("email", email)
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
