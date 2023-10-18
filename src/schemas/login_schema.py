

from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr

class IWalletSignup(BaseModel):
    address: str
    email: EmailStr
    name: str