import logging
from fastapi import Body, Depends, HTTPException, Query, Request, status
from eth_account.messages import encode_defunct
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.security import UserNonce, create_nonce, Token
from web3.auto import w3
from core.security import create_access_token
from schemas.login_schema import IWalletSignup
from schemas.wallet_schema import IWalletCreate
from schemas.user_schema import IUserCreate
from api.deps import get_mail_manager, user_exists
from core.security import create_id_token
from utils.nonce import get_nonce
from fastapi import APIRouter
import crud
import petname


router = APIRouter()

@router.post("/token", response_model=Token)
async def token(
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
            detail=f"Signer address mismatch",
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
            detail=f"Wallet not found",
        )


@router.post("/signup", response_model=UserNonce)
async def wallet_signup(
    request: Request,
    form_data: IWalletSignup = Depends(user_exists),
    fm: FastMail = Depends(get_mail_manager),
):
    wallet_found = await crud.wallet.get_by_address(form_data.address)
    if wallet_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Wallet already used",
        )
    user = await crud.user.create(IUserCreate(
        first_name=petname.generate(words=1),
        last_name=petname.generate(words=1),
        email=form_data.email,
        is_new=True,
    ))
    try:
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
    except Exception as err:
        logging.error(err)
    new_wallet = await crud.wallet.create(IWalletCreate(name=form_data.name, address=form_data.address, user_id=user.id))
    nonce = await create_nonce(new_wallet.user_id)
    return nonce


@router.post("/link", response_model=UserNonce)
async def link_wallet(
    wallet: IWalletCreate = Depends()
):
    new_wallet = await crud.wallet.create(wallet)
    nonce = await create_nonce(new_wallet.user_id)
    return nonce
