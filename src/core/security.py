import string
from datetime import datetime, timedelta
from random import SystemRandom
from typing import Any, Literal, Union

from cryptography.fernet import Fernet
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from redis import Redis

import crud
from core.settings import settings
from utils.nonce import set_nonce
from utils.token import TokenType, get_tokens, set_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(str.encode(settings.ENCRYPT_KEY))

ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int


def create_token(subject: Union[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_id_token(
    user_id: str,
    redis_client: Redis | None,
) -> str:
    id_token_expires = timedelta(days=1)
    id_token = create_token(user_id, expires_delta=id_token_expires)
    await set_token(
        redis_client,
        user_id,
        id_token,
        TokenType.ID,
        id_token_expires,
    )
    return id_token


async def create_access_token(
    user_id: str,
    redis_client: Redis | None,
) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(user_id, expires_delta=access_token_expires)
    refresh_token = create_token(user_id, expires_delta=refresh_token_expires)
    await set_token(
        user_id,
        access_token,
        TokenType.ACCESS,
        access_token_expires,
        redis_client,
    )
    await set_token(
        user_id,
        refresh_token,
        TokenType.REFRESH,
        refresh_token_expires,
        redis_client,
    )
    data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expires.seconds,
    )

    return data


async def refresh_access_token(
    refresh_token: str,
    redis_client: Redis | None,
) -> Token:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid refresh token: {str(e)}",
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail="Could not validate refresh token",
        )

    user_id = payload["sub"]
    valid_refresh_tokens = await get_tokens(user_id, TokenType.REFRESH, redis_client)
    if valid_refresh_tokens and refresh_token not in valid_refresh_tokens:
        raise HTTPException(status_code=403, detail="Unknown refresh token")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user = await crud.user.get(id=user_id)
    if user.is_active:
        access_token = create_token(user_id, expires_delta=access_token_expires)
        await set_token(user.id, access_token, TokenType.ACCESS, access_token_expires, redis_client)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_token_expires.seconds,
        )
    else:
        raise HTTPException(status_code=404, detail="User inactive")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data)
    return data.decode()


def get_content(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()


class UserNonce(BaseModel):
    nonce: str
    user_id: str


async def create_nonce(user_id: str, redis_client: Redis | None) -> UserNonce:
    expires = datetime.utcnow() + timedelta(minutes=5)
    letters = string.ascii_uppercase + string.ascii_lowercase
    nonce = "".join(SystemRandom().choices(letters, k=12))
    await set_nonce(user_id, nonce, expires, redis_client)
    return UserNonce(nonce=nonce, user_id=user_id)
