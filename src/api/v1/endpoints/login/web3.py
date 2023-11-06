from typing import Any, Dict
from uuid import UUID

import petname
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from siwe import SiweMessage, VerificationError
from uuid6 import uuid7

import crud
from core.security import Token, TrustedJWSBearer, JWSBearer, create_nonce, create_token, jws_bearer, revoke_token
from core.settings import settings
from exceptions.common_exception import NameNotFoundException
from middlewares.asql import AsyncSession, get_ctx_session
from models.group_model import GroupEnum
from models.role_model import Role, RoleEnum
from schemas.login_schema import IUserAuthInfo
from schemas.response_schema import IResponse, create_response
from schemas.user_schema import IUserCreate, IUserRead, IUserUpsert
from schemas.wallet_schema import IWalletCreate
from utils.nonce import get_nonce

router = APIRouter()


# class DynamicsJWSBearer(TrustedJWSBearer):
#     def __init__(self):
#         with open(settings.DYNAMICS_PUBLIC_KEY_FILE) as f:
#             super().__init__(f.read(), {"verify_aud": False})


# reusable_jwt_bearer = DynamicsJWSBearer()
reusable_jwt_bearer = JWSBearer()



@router.post("/verify", response_model=IUserAuthInfo)
async def verify(
    request: Request,
    message: str = Body(...),
    signature: str = Body(...),
):
    session_id = request.session.get("siwe", None)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    nonce = await get_nonce(session_id)

    try:
        siwe_message: SiweMessage = SiweMessage(message=message)
        siwe_message.verify(signature, nonce=nonce)
    except VerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    wallet = await crud.wallet.get_by("address", siwe_message.address)
    if not wallet:
        full_name = petname.generate(words=2, separator=" ").split(" ")
        role = await crud.role.get_by("name", RoleEnum.citizen)
        group = await crud.group.get_by("name", GroupEnum.player)
        user = await crud.user.create(
            obj_in=IUserCreate(
                first_name=full_name[0],
                last_name=full_name[-1],
                role_id=role.id,
            )
        )
        await crud.group.add_user_to_group(user=user, group_id=group.id)
        await crud.user.refresh(user)
        wallet = await crud.wallet.create(
            IWalletCreate(chain_id=siwe_message.chain_id, public_key=siwe_message.address, user_id=user.id)
        )
    token = await create_token(wallet.user_id)
    return IUserAuthInfo(user_info=wallet.user, **token.dict())


@router.get("/nonce", response_class=PlainTextResponse)
async def nonce(
    request: Request,
):
    session_id = uuid7()
    request.session["siwe"] = str(session_id)
    nonce = await create_nonce(session_id)
    return nonce


@router.post("/refresh", response_model=Token)
async def refresh(
    jwt: Dict[str, Any] = Depends(jws_bearer),
):
    """
    Gets a new access token using the refresh token for future requests
    """
    data = await create_token(jwt["sub"])
    return data


@router.post("/revoke")
async def revoke(
    jwt: Dict[str, Any] = Depends(jws_bearer),
):
    await revoke_token(jwt["sub"])


@router.post("/token", response_model=Token)
async def token(
    jwt: Dict[str, Any] = Depends(reusable_jwt_bearer),
):
    token = await create_token(jwt["sub"])
    return token


@router.post("/register", response_model=IResponse[IUserRead], status_code=status.HTTP_200_OK)
async def register(
    user: IUserUpsert, jwt: Dict[str, Any] = Depends(reusable_jwt_bearer), db: AsyncSession = Depends(get_ctx_session)
):
    """
    Register a user
    """
    if str(user.id) != jwt["sub"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if user_found := await crud.user.get(id=user.id, db_session=db):
        user_payload = user.dict(exclude_unset=True, exclude_none=True)
        user_found = await crud.user.update(obj_current=user_found, obj_new=user_payload, db_session=db)
    else:
        user_found = await crud.user.create(obj_in=user, db_session=db)

    if user.role is not None:
        if role := await crud.role.get_by("name", user.role, db_session=db):
            user_found.role_id = role.id
        else:
            raise NameNotFoundException(Role, name=user.role)

    # groups = user.groups
    # if groups is not None:
    #     if groups == []:
    #         await crud.user.remove_from_all_groups(user_found, db_session=db)
    #     else:
    #         for group_name in groups:
    #             if group := await crud.group.get_by("name", group_name, db_session=db):
    #                 user_found = await crud.user.add_to_group(user=user_found, group_id=group.id, db_session=db)
    #             else:
    #                 raise NameNotFoundException(Group, name=group_name)

    wallets = user.wallets
    if wallets is not None:
        if wallets == []:
            await crud.wallet.delete_all_user_wallets(user_found.id)
        else:
            for wallet in wallets:
                if wallet_found := await crud.wallet.get(wallet.id, db_session=db):
                    await crud.wallet.update(obj_current=wallet_found, obj_new=wallet, db_session=db)
                else:
                    await crud.wallet.create(wallet, db_session=db)
                if wallet.name == user.primary_wallet:
                    user_found = await crud.user.update(
                        obj_current=user_found, obj_new={"primary_wallet_id": wallet.id}, db_session=db
                    )

    social_accounts = user.social_accounts
    if social_accounts is not None:
        if social_accounts == []:
            await crud.socialaccount.delete_all_user_wallets(user_found.id, db_session=db)
        else:
            for account in social_accounts:
                if account_found := await crud.socialaccount.get(account.id, db_session=db):
                    await crud.socialaccount.update(obj_current=account_found, obj_new=account, db_session=db)
                else:
                    await crud.socialaccount.create(account, db_session=db)

    await db.flush()
    await db.refresh(user_found)
    return create_response(data=user_found)


@router.post("/wallet/unlik", response_model=IUserRead)
async def unlink_wallet(
    jwt: Dict[str, Any] = Depends(reusable_jwt_bearer),
    wallet_id: UUID = Body(...),
):
    user = await crud.user.get(jwt["sub"])
    return await crud.user.unlink_wallet(user, wallet_id)


@router.post("/socialaccount/unlik", response_model=IUserRead)
async def unlink_socialaccounts(
    jwt: Dict[str, Any] = Depends(reusable_jwt_bearer),
    account_id: UUID = Body(...),
):
    user = await crud.user.get(jwt["sub"])
    return await crud.user.unlink_socialaccount(user, account_id)
