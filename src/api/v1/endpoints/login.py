from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from pydantic import EmailStr, ValidationError
from redis.asyncio import Redis

import crud
from api import deps
from api.deps import get_redis_client
from core import security
from core.config import settings
from core.security import get_password_hash, verify_password
from models.user_model import User
from schemas.common_schema import IMetaGeneral, TokenType
from schemas.response_schema import IPostResponseBase, create_response
from schemas.token_schema import RefreshToken, Token, TokenRead
from utils.token import add_token_to_redis, delete_tokens, get_valid_tokens

router = APIRouter()


class OAuth2PasswordRequestForm:
    """Modified from fastapi.security.OAuth2PasswordRequestForm"""

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


async def _access_token(
    email: str,
    password: str,
    redis_client: Redis,
) -> Token:
    user = await crud.user.authenticate(email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Email or Password incorrect")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(user.id, expires_delta=refresh_token_expires)
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )
    valid_access_tokens = await get_valid_tokens(redis_client, user.id, TokenType.ACCESS)
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    valid_refresh_tokens = await get_valid_tokens(redis_client, user.id, TokenType.REFRESH)
    if valid_refresh_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            refresh_token,
            TokenType.REFRESH,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    return data


async def _refresh_token(
    refresh_token: str,
    redis_client: Redis,
) -> Token:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Refresh token invalid")

    if payload["type"] == "refresh":
        user_id = payload["sub"]
        valid_refresh_tokens = await get_valid_tokens(redis_client, user_id, TokenType.REFRESH)
        if valid_refresh_tokens and refresh_token not in valid_refresh_tokens:
            raise HTTPException(status_code=403, detail="Refresh token invalid")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        user = await crud.user.get(id=user_id)
        if user.is_active:
            access_token = security.create_access_token(payload["sub"], expires_delta=access_token_expires)
            valid_access_get_valid_tokens = await get_valid_tokens(redis_client, user.id, TokenType.ACCESS)
            if valid_access_get_valid_tokens:
                await add_token_to_redis(
                    redis_client,
                    user,
                    access_token,
                    TokenType.ACCESS,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                )
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                refresh_token=refresh_token,
                user=user,
            )
        else:
            raise HTTPException(status_code=404, detail="User inactive")
    else:
        raise HTTPException(status_code=404, detail="Incorrect token")


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: Redis = Depends(get_redis_client),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if form_data.grant_type == "password":
        data = await _access_token(form_data.username, form_data.password, redis_client)

    if form_data.grant_type == "refresh_token":
        data = await _refresh_token(form_data.refresh_token, redis_client)
    return data


@router.post("/signin", response_model=IPostResponseBase[Token])
async def login(
    email: EmailStr = Body(...),
    password: str = Body(...),
    meta_data: IMetaGeneral = Depends(deps.get_general_meta),
    redis_client: Redis = Depends(get_redis_client),
) -> Any:
    """
    Login for all users
    """
    data = await _access_token(email, password, redis_client)
    return create_response(meta=meta_data, data=data, message="Login correctly")


@router.post("/signout", response_model=IPostResponseBase[Token])
async def logout(
    redirect_url: str = Query("/"),
    current_user: User = Depends(deps.get_current_user()),
    redis_client: Redis = Depends(get_redis_client),
):
    await delete_tokens(redis_client, current_user, TokenType.ACCESS)
    await delete_tokens(redis_client, current_user, TokenType.REFRESH)
    response = RedirectResponse(url=redirect_url)
    response.delete_cookie("Authorization")
    return response


@router.post("/change-password", response_model=IPostResponseBase[Token])
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(deps.get_current_user()),
    redis_client: Redis = Depends(get_redis_client),
) -> Any:
    """
    Change password
    """

    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Current Password")

    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New Password should be different that the current one",
        )

    new_hashed_password = get_password_hash(new_password)
    await crud.user.update(obj_current=current_user, obj_new={"hashed_password": new_hashed_password})

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(current_user.id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(current_user.id, expires_delta=refresh_token_expires)
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=current_user,
    )

    await delete_tokens(redis_client, current_user, TokenType.ACCESS)
    await delete_tokens(redis_client, current_user, TokenType.REFRESH)
    await add_token_to_redis(
        redis_client,
        current_user,
        access_token,
        TokenType.ACCESS,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await add_token_to_redis(
        redis_client,
        current_user,
        refresh_token,
        TokenType.REFRESH,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return create_response(data=data, message="New password generated")


@router.post("/refresh-token", response_model=IPostResponseBase[TokenRead], status_code=201)
async def refresh_token(
    body: RefreshToken = Body(...),
    redis_client: Redis = Depends(get_redis_client),
) -> Any:
    """
    Gets a new access token using the refresh token for future requests
    """
    data = await _refresh_token(body.refresh_token)
    return create_response(
        data=data,
        message="Access token generated correctly",
    )
