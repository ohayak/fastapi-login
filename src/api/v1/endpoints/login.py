import logging
import random
import string
from datetime import timedelta
from typing import Any, Dict, Literal
from uuid import UUID

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from jose import jwt
from pydantic import EmailStr, ValidationError
from redis.asyncio import Redis

import crud
from api.deps import get_current_user, get_general_meta, get_mail_manager, user_exists
from core import security
from core.settings import settings
from core.security import get_password_hash, verify_password
from exceptions.common_exception import IdNotFoundException
from middlewares.redis import get_ctx_client
from models.user_model import User
from schemas.common_schema import IMetaGeneral, RefreshToken, Token, TokenType
from schemas.response_schema import IResponse, create_response
from schemas.role_schema import IRoleEnum
from schemas.user_schema import IUserCreate, IUserRead, IUserSignup
from utils.token import delete_tokens, get_tokens, set_token

router = APIRouter()

oauth = OAuth()

for idp in ["GOOGLE", "FACEBOOK", "MICROSOFT"]:
    oauth.register(
        name=idp.lower(),
        client_id=getattr(settings, f"{idp}_CLIENT_ID"),
        client_secret=getattr(settings, f"{idp}_CLIENT_SECRET"),
        server_metadata_url=getattr(settings, f"{idp}_CONF_URL"),
        client_kwargs={"scope": "openid email profile"},
    )


class OAuth2PasswordRequestForm:
    """Modified from fastapi.security.OAuth2PasswordRequestForm"""

    def __init__(
        self,
        grant_type: str = Form(regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token


async def _authenticate(email: EmailStr, password: str) -> User:
    user = await crud.user.authenticate(email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Email or Password incorrect")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    return user


async def _id_token(
    user: User,
    redis_client: Redis,
) -> Token:
    id_token_expires = timedelta(days=1)
    id_token = security.create_token(user.id, expires_delta=id_token_expires)
    await set_token(
        redis_client,
        user.id,
        id_token,
        TokenType.ID,
        id_token_expires,
    )
    return id_token


async def _access_token(
    user: User,
    redis_client: Redis,
) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_token(user.id, expires_delta=access_token_expires)
    refresh_token = security.create_token(user.id, expires_delta=refresh_token_expires)
    await set_token(
        redis_client,
        user.id,
        access_token,
        TokenType.ACCESS,
        access_token_expires,
    )
    await set_token(
        redis_client,
        user.id,
        refresh_token,
        TokenType.REFRESH,
        refresh_token_expires,
    )
    data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expires.seconds,
        user=user,
    )

    return data


async def _refresh_token(
    refresh_token: str,
    redis_client: Redis,
) -> Token:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
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
    valid_refresh_tokens = await get_tokens(redis_client, user_id, TokenType.REFRESH)
    if valid_refresh_tokens and refresh_token not in valid_refresh_tokens:
        raise HTTPException(status_code=403, detail="Unknown refresh token")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user = await crud.user.get(id=user_id)
    if user.is_active:
        access_token = security.create_token(user_id, expires_delta=access_token_expires)
        await set_token(
            redis_client,
            user.id,
            access_token,
            TokenType.ACCESS,
            access_token_expires,
        )
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_token_expires.seconds,
            user=user,
        )
    else:
        raise HTTPException(status_code=404, detail="User inactive")


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: Redis = Depends(get_ctx_client),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if form_data.grant_type == "password":
        user = await _authenticate(form_data.username, form_data.password)
        data = await _access_token(user, redis_client)
    elif form_data.grant_type == "refresh_token":
        data = await _refresh_token(form_data.refresh_token, redis_client)
    else:
        raise HTTPException(status_code=400, detail="invalid_grant")
    return data


@router.get("/verify-email", response_model=IResponse[IUserRead])
async def verify_email(
    request: Request,
    user_id: UUID = Query(),
    token: str = Query(),
    fm: FastMail = Depends(get_mail_manager),
    redis_client: Redis = Depends(get_ctx_client),
):
    user: User = await crud.user.get(id=user_id)

    if user is None:
        raise IdNotFoundException(User, user_id)

    valid_tokens = await get_tokens(redis_client, user_id, TokenType.ID)

    if valid_tokens and token not in valid_tokens:
        token = await _id_token(user, redis_client)
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[user.email],
            template_body=dict(
                first_name=user.first_name,
                last_name=user.last_name,
                verification_link=f"{request.url_for('verify_email')}?user_id={user.id}&token={token}",
            ),
            subtype=MessageType.html,
        )
        await fm.send_message(message, template_name="email_verification.jinja2")
        raise HTTPException(status_code=400, detail="Token Expired. Another verification email has been sent.")

    # Mark the user as verified
    user = await crud.user.update(obj_current=user, obj_new={"is_verified": True})

    return create_response(data=user)


@router.post("/signup", response_model=IResponse[IUserRead], status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    fm: FastMail = Depends(get_mail_manager),
    new_user: IUserSignup = Depends(user_exists),
    redis_client: Redis = Depends(get_ctx_client),
):
    """
    Creates a new user with user role
    """
    role = await crud.role.get_role_by_name(name=IRoleEnum.user)
    new_user = IUserCreate.from_orm(new_user)
    user = await crud.user.create_with_role(obj_in=new_user, role_id=role.id)
    try:
        token = await _id_token(user, redis_client)
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[user.email],
            template_body=dict(
                first_name=user.first_name,
                last_name=user.last_name,
                verification_link=f"{request.url_for('verify_email')}?user_id={user.id}&token={token}",
            ),
            subtype=MessageType.html,
        )
        await fm.send_message(message, template_name="email_verification.jinja2")
    except Exception as err:
        logging.error(err)
    return create_response(data=user)


@router.post("/signin", response_model=Token)
async def signin(
    email: EmailStr = Body(...),
    password: str = Body(...),
    meta_data: IMetaGeneral = Depends(get_general_meta),
    redis_client: Redis = Depends(get_ctx_client),
) -> Any:
    """
    Login for all users
    """
    user = await _authenticate(email, password)
    data = await _access_token(user, redis_client)
    return data


@router.post("/signout")
async def signout(
    redirect_url: str = Query("/"),
    current_user: User = Depends(get_current_user()),
    redis_client: Redis = Depends(get_ctx_client),
):
    await delete_tokens(redis_client, current_user.id, TokenType.ACCESS)
    await delete_tokens(redis_client, current_user.id, TokenType.REFRESH)
    response = RedirectResponse(url=redirect_url)
    response.delete_cookie("Authorization")
    return response


@router.get("/reset-password", response_model=IUserRead)
async def reset_password(
    email: EmailStr = Query(),
    fm: FastMail = Depends(get_mail_manager),
):
    """
    Reset password
    """
    current_user = await crud.user.get_by_email(email=email)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    new_password = "".join(random.choice(string.printable) for i in range(8))
    new_hashed_password = get_password_hash(new_password)
    await crud.user.update(obj_current=current_user, obj_new={"hashed_password": new_hashed_password})

    message = MessageSchema(
        subject="Password Reset",
        recipients=[current_user.email],
        template_body=dict(
            first_name=current_user.first_name,
            temporary_password=new_password,
        ),
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="password_reset.jinja2")
    return create_response(data=current_user)


@router.post("/change-password", response_model=Token)
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user()),
    redis_client: Redis = Depends(get_ctx_client),
):
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
    access_token = security.create_token(current_user.id, expires_delta=access_token_expires)
    refresh_token = security.create_token(current_user.id, expires_delta=refresh_token_expires)

    await delete_tokens(redis_client, current_user.id, TokenType.ACCESS)
    await delete_tokens(redis_client, current_user.id, TokenType.REFRESH)
    await set_token(
        redis_client,
        current_user.id,
        access_token,
        TokenType.ACCESS,
        access_token_expires,
    )
    await set_token(
        redis_client,
        current_user.id,
        refresh_token,
        TokenType.REFRESH,
        refresh_token_expires,
    )

    data = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expires.seconds,
        user=current_user,
    )

    return data


@router.post("/refresh-token", response_model=Token, status_code=201)
async def refresh_token(
    body: RefreshToken = Body(...),
    redis_client: Redis = Depends(get_ctx_client),
) -> Any:
    """
    Gets a new access token using the refresh token for future requests
    """
    data = await _refresh_token(body.refresh_token, redis_client)
    return data


@router.get("/{idp}")
async def login_via_idp(idp: Literal["google", "facebook", "microsoft"], request: Request):
    redirect_url = request.url_for("auth_via_idp", idp=idp)
    return await oauth[idp].authorize_redirect(request, redirect_url)


@router.get("/{idp}/auth", include_in_schema=False)
async def auth_via_idp(idp: str, request: Request, redis_client: Redis = Depends(get_ctx_client)):
    try:
        token = await oauth[idp].authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(
            status_code=400,
            detail=error.error,
        )

    userinfo: Dict = token["userinfo"]
    userobj = User(first_name=userinfo["given_name"], last_name=userinfo["family_name"], email=userinfo.get("email"))
    user = await crud.user.get_by_email(userobj.email)
    if not user:
        user = await crud.user.create(obj_in=userobj)
    user = await crud.user.add_social_login(user, idp)
    data = await _access_token(user, redis_client)
    return data
