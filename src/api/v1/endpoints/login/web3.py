from typing import Any, Dict, Optional

import httpx
import petname
from eth_account.messages import encode_defunct
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request, status
from fastapi.security.utils import get_authorization_scheme_param
from jose import exceptions, jwt
from web3.auto import w3

import crud
from api.deps import get_current_user
from core.security import Token, UserNonce, create_access_token, create_nonce, refresh_access_token
from models.group_model import GroupEnum
from models.role_model import RoleEnum
from models.user_model import User
from schemas.login_schema import IUserAuthInfo
from schemas.user_schema import IUserCreate
from schemas.wallet_schema import IWalletCreate
from utils.nonce import get_nonce

router = APIRouter()


@router.post("/verify", response_model=Token)
async def verify(
    address: str = Body(...),
    signature: str = Body(...),
):
    wallet = await crud.wallet.get_by_address(address)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    try:
        nonce = await get_nonce(wallet.user_id)
        message = encode_defunct(text=nonce)
        signer_address = w3.eth.account.recover_message(message, signature=signature)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not recover message: {e}",
        )

    if signer_address == address:
        access_token = await create_access_token(wallet.user_id)
        return access_token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signer address mismatch",
        )


@router.get("/nonce", response_model=UserNonce)
async def nonce(address: str = Query(...)):
    wallet_found = await crud.wallet.get_by_address(address)
    if wallet_found:
        nonce = await create_nonce(wallet_found.user_id)
        return nonce
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )


class Web3AuthIdTokenBearer:
    def __init__(self, jwks_url: str):
        response = httpx.get(jwks_url)
        self.jwks = response.json()

    def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        algorithm = jwt.get_unverified_header(param).get("alg")

        try:
            token = jwt.decode(param, self.jwks, algorithms=algorithm, options={"verify_aud": False})
        except exceptions.JWTError as e:
            raise HTTPException(
                status_code=403,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token


wallet_bearer_token = Web3AuthIdTokenBearer("https://authjs.web3auth.io/jwks")
social_bearer_token = Web3AuthIdTokenBearer("https://api-auth.web3auth.io/jwks")


@router.post("/auth", response_model=IUserAuthInfo)
async def auth(
    request: Request,  # type: ignore
    flow: str = Form(regex="social|wallet"),
    public_address: str = Form(...),
):
    if flow == "social":
        token = social_bearer_token(request)
        wallet_address = token["wallets"][0]["public_key"]
    elif flow == "wallet":
        token = wallet_bearer_token(request)
        wallet_address = token["wallets"][0]["address"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_flow")

    wallet_type = token["wallets"][0]["type"]

    if wallet_address != public_address:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wallet address mismatch",
        )

    wallet = await crud.wallet.get_by_address(wallet_address)
    if not wallet:
        random_name = petname.generate(words=2, separator=" ")
        full_name = token.get("name", random_name).split(" ")
        role = await crud.role.get_by_name(RoleEnum.citizen)
        group = await crud.group.get_by_name(GroupEnum.player)
        user = await crud.user.create(
            obj_in=IUserCreate(
                first_name=full_name[0],
                last_name=full_name[-1],
                email=token.get("email"),
                email_verified=token.get("email") is not None,
                role_id=role.id,
            )
        )
        await crud.group.add_user_to_group(user=user, group_id=group.id)
        await crud.user.refresh(user)
        if social_media := token.get("verifier"):
            # AggregateVerifiers are named like: main-google, main-apple ...
            await crud.user.add_social_login(user=user, social_login=social_media.split("-")[-1])
        wallet = await crud.wallet.create(IWalletCreate(type=wallet_type, address=wallet_address, user_id=user.id))

    access_token = await create_access_token(wallet.user_id)
    return IUserAuthInfo(user_info=wallet.user, **access_token.dict())


@router.post("/refresh-token", response_model=Token, status_code=201)
async def refresh_token(
    refresh_token: str = Body(...),
    current_user: User = Depends(get_current_user()),
):
    """
    Gets a new access token using the refresh token for future requests
    """
    data = await refresh_access_token(refresh_token)
    return data
