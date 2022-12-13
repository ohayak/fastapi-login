import contextlib

from fastapi import APIRouter, Depends, Form, Request, Response, Query
from fastapi.responses import RedirectResponse

from crud.schema import BaseApiOut
from crud.utils import schema_create_by_schema
from services.auth import auth

from .schemas import UserLoginOut, UserInfo

router = APIRouter(prefix="/auth")


router.dependencies.insert(0, Depends(auth.backend.authenticate))


@router.get("/userinfo", description="User Profile", response_model=BaseApiOut[UserInfo])
@auth.requires()
async def userinfo(request: Request):
    return BaseApiOut(data=request.user)


@router.get("/logout", description="Logout", response_model=BaseApiOut)
@auth.requires()
async def user_logout(request: Request, redirect_url: str = Query("/")):
    token_value = request.auth.backend.get_user_token(request)
    with contextlib.suppress(Exception):
        await auth.backend.token_store.destroy_token(token=token_value)
    response = RedirectResponse(url=redirect_url)
    response.delete_cookie("Authorization")
    return response


@router.post("/token", description="OAuth2 Token", response_model=BaseApiOut[UserLoginOut])
async def oauth_token(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    if request.scope.get("user") is None:
        request.scope["user"] = await request.auth.authenticate_user(username=username, password=password)
    if request.scope.get("user") is None:
        return BaseApiOut(status=-1, msg="Incorrect username or password!")
    token_info = UserLoginOut.parse_obj(request.user)
    token_info.access_token = await request.auth.backend.token_store.write_token(request.user.dict())
    response.set_cookie("Authorization", f"bearer {token_info.access_token}")
    return BaseApiOut(data=token_info)
