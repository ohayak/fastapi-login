import contextlib
import logging

from fastapi import APIRouter, Depends, Form, Query, Request, Response, Body, HTTPException
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.schema import BaseApiOut
from crud.utils import schema_create_by_schema
from services.auth import auth
from services.auth.models import User
from services.database import gen_auth_async_session
from .schemas import UserInfo, UserLoginOut, UserRegIn

router = APIRouter(prefix="/auth")


router.dependencies.insert(0, Depends(auth.backend.authenticate))


@router.get("/userinfo", description="User Profile", response_model=User)
@auth.requires()
async def userinfo(request: Request):
    logging.debug(request.user)
    return request.user


@router.get("/logout", description="Logout", response_model=BaseApiOut)
@auth.requires()
async def user_logout(request: Request, redirect_url: str = Query("/")):
    token_value = request.auth.backend.get_user_token(request)
    with contextlib.suppress(Exception):
        await auth.backend.token_store.destroy_token(token=token_value)
    response = RedirectResponse(url=redirect_url)
    response.delete_cookie("Authorization")
    return response


@router.post("/token", description="OAuth2 Token", response_model=UserLoginOut)
async def oauth_token(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    if request.scope.get("user") is None:
        request.scope["user"] = await request.auth.authenticate_user(username=username, password=password)
    if request.scope.get("user") is None:
        return BaseApiOut(status=-1, msg="Incorrect username or password!")
    token_info = UserLoginOut.parse_obj(request.user)
    token_info.access_token = await request.auth.backend.token_store.write_token(request.user.dict())
    response.set_cookie("Authorization", f"bearer {token_info.access_token}")
    return token_info


# @router.post("/register", description="OAuth2 Token", response_model=BaseApiOut[UserLoginOut])
async def register(request: Request, payload: UserRegIn, db: AsyncSession = Depends(gen_auth_async_session)):
    print(payload)
    result = await db.scalar(db.select(User).where(User.username == payload.username))
    if result:
        raise HTTPException(status_code=409, detail=f"{payload.username} already exits")

    new_user = User(username=payload.username,
        password=CryptContext(schemes=["bcrypt"], deprecated="auto").hash(payload.password))

    return BaseApiOut(data=new_user)
