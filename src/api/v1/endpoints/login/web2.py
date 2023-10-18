import logging
import random
import string
from datetime import timedelta
from typing import Any, Dict, Literal
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from jose import jwt
from pydantic import EmailStr, ValidationError
from redis.asyncio import Redis

import crud
from api.deps import get_current_user, get_general_meta, get_mail_manager, user_exists
from core.security import get_password_hash, verify_password, TokenType, Token
from exceptions.common_exception import IdNotFoundException
from middlewares.redis import get_ctx_client
from models.user_model import User
from schemas.response_schema import IResponse, create_response
from schemas.role_schema import IRoleEnum
from schemas.user_schema import IUserCreate, IUserRead, IUserSignup
from core.security import create_access_token, create_id_token, refresh_access_token
from utils.token import delete_tokens, get_tokens, set_token

router = APIRouter()

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or Password incorrect")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")
    return user

@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if form_data.grant_type == "password":
        user = await _authenticate(form_data.username, form_data.password)
        data = await create_access_token(user.id)
    elif form_data.grant_type == "refresh_token":
        data = await refresh_access_token(form_data.refresh_token)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant")
    return data


@router.post("/signup", response_model=IResponse[IUserRead], status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    fm: FastMail = Depends(get_mail_manager),
    new_user: IUserSignup = Depends(user_exists),
):
    """
    Creates a new user with user role
    """
    role = await crud.role.get_by_name(name=IRoleEnum.user)
    new_user = IUserCreate.from_orm(new_user)
    user = await crud.user.create_with_role(obj_in=new_user, role_id=role.id)
    try:
        token = await create_id_token(user.id)
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
):
    """
    Login for all users
    """
    user = await _authenticate(email, password)
    data = await create_access_token(user.id)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Current Password")

    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New Password should be different that the current one",
        )

    new_hashed_password = get_password_hash(new_password)
    await crud.user.update(obj_current=current_user, obj_new={"hashed_password": new_hashed_password})

    await delete_tokens(current_user.id, TokenType.ACCESS, redis_client)
    await delete_tokens(current_user.id, TokenType.REFRESH, redis_client)

    data = await create_access_token(current_user.id, redis_client)
    return data


@router.post("/refresh-token", response_model=Token, status_code=201)
async def refresh_token(
    refresh_token: str = Body(...),
):
    """
    Gets a new access token using the refresh token for future requests
    """
    data = await refresh_access_token(refresh_token)
    return data

