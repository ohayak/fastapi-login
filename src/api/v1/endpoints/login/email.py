from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

import crud
from api.deps import get_current_user, get_mail_manager
from core.security import TokenType, create_token, jwt_decode
from exceptions.common_exception import IdNotFoundException
from models.group_model import GroupEnum
from models.user_model import User
from schemas.response_schema import IResponse, create_response
from schemas.user_schema import IUserRead
from utils.token import get_tokens

router = APIRouter()


@router.get("/verify-email")
async def verify_email_callback(
    request: Request,
    redirect_url: str = Query(),
    token: str = Query(),
    fm: FastMail = Depends(get_mail_manager),
):
    user_id = jwt_decode(token)["sub"]
    user = await crud.user.get(id=user_id)

    if user is None:
        raise IdNotFoundException(User, user_id)

    valid_tokens = await get_tokens(user_id, TokenType.ID)

    if valid_tokens and token not in valid_tokens:
        token = await create_token(user.id)
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[user.email],
            template_body=dict(
                first_name=user.first_name,
                last_name=user.last_name,
                verification_link=f"{request.url_for('verify_email')}?token={token}&redirect_url={redirect_url}",
            ),
            subtype=MessageType.html,
        )
        await fm.send_message(message, template_name="email_verification.jinja2")
        return HTMLResponse(content="Token Expired. Another verification email has been sent.")

    # Mark the user as verified
    user = await crud.user.update(obj_current=user, obj_new={"email_verified": True})

    if redirect_url:
        return RedirectResponse(url=redirect_url)
    else:
        return HTMLResponse(content="Email verified successfully")


@router.post("/verify-email")
async def verify_email(
    request: Request,
    user_id: UUID = Body(...),
    redirect_url: str = Body(),
    current_user: User = Depends(get_current_user()),
    fm: FastMail = Depends(get_mail_manager),
):
    if GroupEnum.admin not in current_user.groups and current_user.id != user_id:
        # non admin user is trying to update another user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user = await crud.user.get(id=user_id)

    if user is None:
        raise IdNotFoundException(User, user_id)

    token = await create_token(user.id)
    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[user.email],
        template_body=dict(
            first_name=user.first_name,
            last_name=user.last_name,
            verification_link=f"{request.url_for('verify_email')}?token={token}&redirect_url={redirect_url}",
        ),
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="email_verification.jinja2")


@router.post("/update-email", response_model=IResponse[IUserRead])
async def update_email(
    request: Request,
    user_id: UUID = Body(...),
    email: EmailStr = Body(...),
    redirect_url: str = Body(...),
    verified: bool = Body(False),
    current_user: User = Depends(get_current_user()),
    fm: FastMail = Depends(get_mail_manager),
):
    if GroupEnum.admin not in current_user.groups and current_user.id != user_id:
        # non admin user is trying to update another user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user = await crud.user.get(id=user_id)

    if user is None:
        raise IdNotFoundException(User, user_id)

    user = await crud.user.update(obj_current=user, obj_new={"email": email, "email_verified": verified})

    if not verified:
        token = await create_token(user.id)
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[user.email],
            template_body=dict(
                first_name=user.first_name,
                last_name=user.last_name,
                verification_link=f"{request.url_for('verify_email')}?token={token}&redirect_url={redirect_url}",
            ),
            subtype=MessageType.html,
        )
        await fm.send_message(message, template_name="email_verification.jinja2")

    return create_response(data=user)
