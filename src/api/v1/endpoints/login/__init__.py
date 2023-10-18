from fastapi import APIRouter

from api.v1.endpoints.login import email, web2, wallet

router = APIRouter()
router.include_router(email.router, tags=["login"])
router.include_router(web2.router, prefix="/web2", tags=["login"])
router.include_router(wallet.router, prefix="/wallet", tags=["login"])

