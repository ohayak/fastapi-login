from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig, FastMail

import crud
from core.security import jwt_decode
from core.settings import settings
from models.group_model import GroupEnum
from models.role_model import RoleEnum
from models.user_model import User
from schemas.common_schema import IMetaGeneral
from schemas.user_schema import IUserCreate, IUserSignup
from utils.token import TokenType, get_tokens


async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/oauth2/token")


def get_current_user(allowed_roles: List[RoleEnum] = [], allowed_groups: List[GroupEnum] = []) -> User:
    async def current_user(
        token: str = Depends(reusable_oauth2),
    ) -> User:
        payload = jwt_decode(token)
        user_id = payload["sub"]
        valid_access_tokens = await get_tokens(user_id, TokenType.ACCESS)
        if not valid_access_tokens or token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unknown token",
            )
        user: User = await crud.user.get(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        if allowed_roles:
            is_valid_role = False
            for role in allowed_roles:
                if role == user.role.name:
                    is_valid_role = True
            if not is_valid_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role {allowed_roles} is required for this action",
                )

        if allowed_groups:
            is_valid_group = False
            for group in allowed_groups:
                if group in user.groups:
                    is_valid_group = True
            if not is_valid_group:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Group {allowed_groups} is required for this action",
                )

        return user

    return current_user


async def user_exists(new_user: IUserSignup | IUserCreate) -> IUserCreate:
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


def get_mail_manager() -> FastMail:
    conf = ConnectionConfig(
        MAIL_USERNAME="mail-service-user",
        MAIL_PASSWORD="mail-service-password",
        MAIL_FROM="noreply@fast.api",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.main.service",
        MAIL_FROM_NAME="Dev",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="templates",
    )
    return FastMail(conf)
