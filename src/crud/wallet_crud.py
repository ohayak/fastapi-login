from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from middlewares.asql import get_ctx_session
from models.wallet_model import Wallet
from schemas.wallet_schema import IWalletCreate, IWalletUpdate


class CRUDWallet(CRUDBase[Wallet, IWalletCreate, IWalletUpdate]):
    async def delete_all_user_wallets(self, user_id: UUID, db_session: Optional[AsyncSession] = None):
        db_session = db_session or get_ctx_session()
        response = await db_session.execute(select(self.model).where(self.model.user_id == user_id))
        for obj in response.scalars().all():
            await db_session.delete(obj)
        await db_session.flush()


wallet = CRUDWallet(Wallet)
