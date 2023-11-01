import logging
import random
import string

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from redis.asyncio import Redis

import crud
from api.deps import get_current_user, get_mail_manager, user_exists
from core.security import Token, TokenType, create_token, get_password_hash, refresh_token, verify_password
from middlewares.redis import get_ctx_client
from models.role_model import RoleEnum
from models.user_model import User
from schemas.response_schema import create_response
from schemas.user_schema import IUserCreate, IUserRead, IUserSignup
from utils.token import delete_tokens

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


@router.post("/auth", response_model=Token)
async def auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get a token for future requests
    """
    if form_data.grant_type == "password":
        user = await _authenticate(form_data.username, form_data.password)
        data = await create_token(user.id)
    elif form_data.grant_type == "refresh_token":
        data = await refresh_token(form_data.refresh_token)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant")
    return data


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    fm: FastMail = Depends(get_mail_manager),
    new_user: IUserSignup = Depends(user_exists),
):
    """
    Creates a new user with user role
    """
    role = await crud.role.get_by("name", RoleEnum.user)
    new_user = IUserCreate.from_orm(new_user)
    new_user.role_id = role.id
    user = await crud.user.create(obj_in=new_user)
    try:
        token = await create_token(user.id)
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
    data = await create_token(user.id)
    return data


@router.post("/signin", response_model=Token)
async def signin(
    email: EmailStr = Body(...),
    password: str = Body(...),
):
    """
    Login for all users
    """
    user = await _authenticate(email, password)
    data = await create_token(user.id)
    return data


@router.post("/signout")
async def signout(
    redirect_url: str = Query("/"),
    current_user: User = Depends(get_current_user()),
):
    await delete_tokens(current_user.id, TokenType.JWT)
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
    current_user = await crud.user.get_by("email", email)
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

    await delete_tokens(current_user.id, TokenType.JWT, redis_client)

    data = await create_token(current_user.id, redis_client)
    return data


@router.get("/userinfo", response_model=IUserRead)
async def userinfo(
    current_user: User = Depends(get_current_user()),
):
    """
    Returns the user's information
    """
    return current_user


@router.get("/.well-known/openid-configuration")
async def well_known(request: Request):
    base_url = str(request.url).removesuffix("/.well-known/openid-configuration")
    return {
        "issuer": base_url,
        "token_endpoint": base_url + "/auth",
        "authorization_endpoint": base_url + "/auth",
        "userinfo_endpoint": base_url + "/userinfo",
        "response_types_supported": ["id_token", "token id_token"],
        "id_token_signing_alg_values_supported": ["HS256"],
        "response_modes_supported": ["query"],
        "subject_types_supported": ["public", "pairwise"],
        "grant_types_supported": ["password"],
        "claim_types_supported": ["normal"],
        "claims_parameter_supported": True,
        "claims_supported": ["sub", "email", "first_name", "last_name"],
        "request_parameter_supported": False,
        "request_uri_parameter_supported": False,
        "scopes_supported": ["openid", "profile"],
    }
