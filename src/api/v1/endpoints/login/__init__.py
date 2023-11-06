from fastapi import APIRouter

from api.v1.endpoints.login import email, oauth2, web3

router = APIRouter()
router.include_router(email.router, tags=["login"])
router.include_router(web3.router, prefix="/web3", tags=["login/web3"])
router.include_router(oauth2.router, prefix="/oauth2", tags=["login/oauth2"], include_in_schema=False)
