from typing import Dict, Literal
from fastapi import APIRouter, Depends, HTTPException, Request

from authlib.integrations.starlette_client import OAuth, OAuthError

from core.settings import settings
import crud
from models.user_model import User
from core.security import create_access_token

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


@router.get("/{idp}")
async def login_via_idp(idp: Literal["google", "facebook", "microsoft"], request: Request):
    redirect_url = request.url_for("auth_via_idp", idp=idp)
    return await oauth[idp].authorize_redirect(request, redirect_url)


@router.get("/{idp}/auth", include_in_schema=False)
async def auth_via_idp(idp: str, request: Request):
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
    data = await create_access_token(user.id)
    return data