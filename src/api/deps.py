from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from redis.asyncio import Redis, from_url

import crud
from core import security
from core.config import settings
from middlewares.redis import get_ctx_client
from models.playlist_model import Playlist
from models.user_model import User
from schemas.common_schema import IMetaGeneral, TokenType
from schemas.stream_schema import IStreamCreate
from schemas.user_schema import IUserCreate, IUserRead
from utils.token import get_tokens


async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_current_user(required_roles: List[str] = None) -> User:
    async def current_user(
        token: str = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_ctx_client),
    ) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        except jwt.JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid access token: {str(e)}",
            )
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate access token",
            )
        user_id = payload["sub"]
        valid_access_tokens = await get_tokens(redis_client, user_id, TokenType.ACCESS)
        if not valid_access_tokens or token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown token",
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
                    detail=f"Role {required_roles} is required for this action",
                )

        return user

    return current_user


async def user_exists(new_user: IUserCreate) -> IUserCreate:
    user = await crud.user.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    return new_user


async def is_valid_user(user_id: UUID) -> User:
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")

    return user
