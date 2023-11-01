from typing import Optional
from uuid import UUID

from sqlmodel import select

from crud.base_crud import CRUDBase
from middlewares.asql import AsyncSession, get_ctx_session
from models.socialaccount_model import SocialAccount
from schemas.socialaccount_schema import ISocialAccountCreate, ISocialAccountUpdate


class CRUDSocialAccount(CRUDBase[SocialAccount, ISocialAccountCreate, ISocialAccountUpdate]):
    async def delete_all_user_socialaccounts(self, user_id: UUID, db_session: Optional[AsyncSession] = None):
        db_session = db_session or get_ctx_session()
        response = await db_session.execute(select(self.model).where(self.model.user_id == user_id))
        for obj in response.scalars().all():
            await db_session.delete(obj)
        db_session.flush()


socialaccount = CRUDSocialAccount(SocialAccount)
