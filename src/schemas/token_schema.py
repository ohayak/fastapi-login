from pydantic import BaseModel

from .user_schema import IUserRead


class TokenRead(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class Token(TokenRead):
    refresh_token: str
    user: IUserRead


class RefreshToken(BaseModel):
    refresh_token: str
