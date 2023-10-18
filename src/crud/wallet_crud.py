from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDBase
from middlewares.asql import get_ctx_session
from models.wallet_model import Wallet
from models.user_model import User
from schemas.wallet_schema import IWalletCreate, IWalletUpdate


class CRUDWallet(CRUDBase[Wallet, IWalletCreate, IWalletUpdate]):
    async def get_by_name(self, user_id: UUID, name: str, db_session: Optional[AsyncSession] = None) -> Optional[Wallet]:
        db_session = db_session or get_ctx_session()
        wallet = await db_session.execute(select(Wallet).where((Wallet.user_id == user_id) & (Wallet.name == name)))
        return wallet.scalar_one_or_none()
    
    async def get_by_address(self, address: str, db_session: Optional[AsyncSession] = None) -> Optional[Wallet]:
        db_session = db_session or get_ctx_session()
        wallet = await db_session.execute(select(Wallet).where(Wallet.address == address))
        return wallet.scalar_one_or_none()

wallet = CRUDWallet(Wallet)
