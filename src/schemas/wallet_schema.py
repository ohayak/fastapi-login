from uuid import UUID

from models.wallet_model import WalletBase
from utils.partial import optional


class IWalletCreate(WalletBase):
    pass


class IWalletCreateWithId(WalletBase):
    id: UUID


# All these fields are optional
@optional
class IWalletUpdate(WalletBase):
    pass


class IWalletRead(WalletBase):
    pass
