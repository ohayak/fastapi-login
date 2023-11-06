from fastapi import APIRouter, Request

from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from core.settings import settings

from api.v1 import api_router as api_v1


security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "docs")
    correct_password = secrets.compare_digest(credentials.password, "docs")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

router = APIRouter(prefix="/{version}", dependencies=[Depends(get_current_username)])



@router.get("/docs", include_in_schema=False)
async def get_swagger_documentation(version: str):
    return get_swagger_ui_html(openapi_url=f"./openapi.json", title="docs")


@router.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(version: str):
    return get_redoc_html(openapi_url=f"./openapi.json", title="docs")


@router.get("/openapi.json", include_in_schema=False)
async def openapi(version: str):
    if version == "v1":
        return get_openapi(title=settings.API_TITLE, version=version, routes=api_v1.routes)
    else:
        raise HTTPException(status_code=404, detail=f"API version {version} not found")
