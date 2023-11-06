from typing import Any, Dict, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi_mail import ConnectionConfig, FastMail

import crud
from core.security import JWSBearer
from models.user_model import User
from schemas.common_schema import IMetaGeneral
from schemas.user_schema import IUserCreate, IUserSignup


async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


def get_current_user(
    bearer_token: HTTPBearer = JWSBearer(),
    required_scopes: List[str] = [],
) -> User:
    async def current_user(
        jwt_payload: Dict[str, Any] = Depends(bearer_token),
    ) -> User:
        user: User = await crud.user.get(id=jwt_payload["sub"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        if required_scopes:
            if user_scopes := jwt_payload.get("scopes"):
                if required_scopes not in user_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have enough permissions for this action",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Missing scopes",
                )

        return user

    return current_user


async def user_exists(new_user: IUserSignup | IUserCreate) -> IUserCreate:
    user = await crud.user.get_by("email", new_user.email)
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
