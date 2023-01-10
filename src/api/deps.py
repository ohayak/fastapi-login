from typing import AsyncGenerator, List
from uuid import UUID

import aioredis
from aioredis import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

import crud
from core import security
from core.config import settings
from db.session import SessionLocal, data_session_by_schema
from models.user_model import User
from schemas.common_schema import IMetaGeneral, TokenType
from schemas.user_schema import IUserCreate, IUserRead
from utils.minio_client import MinioClient
from utils.token import get_valid_tokens

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


async def get_redis_client() -> Redis:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_db_by_schema(schema: str = None) -> AsyncGenerator[AsyncSession, None]:
    async with data_session_by_schema(schema) as session:
        yield session


async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


def get_current_user(required_roles: List[str] = None) -> User:
    async def current_user(
        token: str = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_redis_client),
    ) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user_id = payload["sub"]
        valid_access_tokens = await get_valid_tokens(redis_client, user_id, TokenType.ACCESS)
        if valid_access_tokens and token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user: User = await crud.user.get(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        if required_roles:
            is_valid_role = False
            for role in required_roles:
                if role == user.role.name:
                    is_valid_role = True

            if not is_valid_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"""Role "{required_roles}" is required for this action""",
                )

        return user

    return current_user


def minio_auth() -> MinioClient:
    # minio_client = MinioClient(
    #     access_key=settings.MINIO_ROOT_USER,
    #     secret_key=settings.MINIO_ROOT_PASSWORD,
    #     bucket_name=settings.MINIO_BUCKET,
    #     minio_url=settings.MINIO_URL,
    # )
    # return minio_client
    raise NotImplementedError()


async def user_exists(new_user: IUserCreate) -> IUserCreate:
    user = await crud.user.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    return new_user


async def is_valid_user(user_id: UUID) -> IUserRead:
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")

    return user
