from fastapi import APIRouter

from api.v1.endpoints.login import email, web3

router = APIRouter()
router.include_router(email.router, tags=["login"])
router.include_router(web3.router, prefix="/web3", tags=["login/web3"])
