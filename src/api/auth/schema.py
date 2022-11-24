import string
from typing import Optional
from pydantic import EmailStr, Field, validator
from pydantic import BaseModel
from utils.model import AllOptional


class SearchReq(BaseModel):
    query: str = Field(max_length=80)


# class OrganizationPatchReq(metaclass=AllOptional):
#     pass


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(User):
    hashed_password: str


class TokenData:
    username: str | None = None
