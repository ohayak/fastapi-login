from uuid import UUID
from fastapi import Body, Depends, HTTPException, Query, Request, status
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.security import TokenType, create_access_token, create_id_token
from exceptions.common_exception import IdNotFoundException
from models.user_model import User
from schemas.response_schema import IResponse, create_response
from schemas.user_schema import IUserRead
from utils.token import get_tokens
from utils.nonce import get_nonce
from fastapi import APIRouter
import crud
from api.deps import get_current_user, get_general_meta, get_mail_manager, user_exists





router = APIRouter()


@router.get("/verify-email", response_model=IResponse[IUserRead])
async def verify_email(
    request: Request,
    user_id: UUID = Query(),
    token: str = Query(),
    fm: FastMail = Depends(get_mail_manager),
):
    user = await crud.user.get(id=user_id)

    if user is None:
        raise IdNotFoundException(User, user_id)

    valid_tokens = await get_tokens(user_id, TokenType.ID)

    if valid_tokens and token not in valid_tokens:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired. Another verification email has been sent.")

    # Mark the user as verified
    user = await crud.user.update(obj_current=user, obj_new={"is_verified": True})

    return create_response(data=user)