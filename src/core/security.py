import string
from datetime import datetime, timedelta
from random import SystemRandom
from typing import Any, Dict, Literal, Mapping
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import exceptions, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from redis import Redis

from core.settings import settings
from utils.nonce import set_nonce
from utils.token import TokenType, delete_tokens, get_tokens, set_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(str.encode(settings.ENCRYPT_KEY))


class Token(BaseModel):
    jwt: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int


def jwt_encode(claims: Dict[str, Any]) -> str:
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def jwt_decode(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )


async def create_token(
    user_id: str,
    redis_client: Redis | None = None,
) -> Token:
    expires_in = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    expire_date = datetime.utcnow() + expires_in
    claims = {"exp": expire_date, "sub": str(user_id)}
    encoded_jwt = jwt_encode(claims)
    await set_token(
        user_id,
        encoded_jwt,
        TokenType.JWT,
        expires_in,
        redis_client,
    )
    data = Token(
        jwt=encoded_jwt,
        expires_in=expires_in.seconds,
    )
    return data


async def refresh_token(
    token: str,
    redis_client: Redis | None = None,
) -> Token:
    try:
        payload = jwt_decode(token)
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

    user_id = payload["sub"]
    valid_tokens = await get_tokens(user_id, TokenType.JWT, redis_client)
    if valid_tokens and token not in valid_tokens:
        raise HTTPException(status_code=403, detail="Invalid Token")

    new_token = await create_token(user_id, redis_client)
    return new_token


async def revoke_token(
    user_id: str,
    redis_client: Redis | None = None,
):
    await delete_tokens(user_id, TokenType.JWT, redis_client)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data)
    return data.decode()


def get_content(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()


async def create_nonce(session_id: UUID, redis_client: Redis | None = None) -> str:
    expires = timedelta(minutes=5)
    letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    nonce = "".join(SystemRandom().choices(letters, k=12))
    await set_nonce(session_id, nonce, expires, redis_client)
    return nonce


class TrustedJWSBearer(HTTPBearer):
    def __init__(self, key: str | bytes | Mapping[str, Any], options: Mapping[str, Any] | None = None, **kwargs):
        self.key = key
        self.options = options
        super().__init__(**kwargs)

    def __call__(self, request: Request) -> Dict[str, Any]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        algorithm = jwt.get_unverified_header(param).get("alg")

        try:
            jwt_payload = jwt.decode(param, self.key, algorithms=algorithm, options=self.options)
        except exceptions.JWTError as e:
            raise HTTPException(
                status_code=403,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return jwt_payload


class JWSBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Dict[str, Any]:
        auth = super().__call__(request)
        token = auth.credentials
        jwt_payload = jwt_decode(auth.credentials)
        user_id = jwt_payload["sub"]
        valid_tokens = await get_tokens(user_id, TokenType.JWT)
        if not valid_tokens or token not in valid_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalide token",
            )
        return jwt_payload
