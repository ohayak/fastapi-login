from fastapi import APIRouter

from api.v1.endpoints.login import email, web3, oauth2

router = APIRouter()
router.include_router(email.router, tags=["login/email"])
router.include_router(oauth2.router, prefix="/oauth2", tags=["login/oauth2"])
router.include_router(web3.router, prefix="/web3", tags=["login/web3"])
