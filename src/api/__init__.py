from .auth.routes import router as auth_router
from .jobs.routes import router as jobs_router
from .users.routes import router as users_router
from fastapi import APIRouter


__all__ = [ "router" ]

router = APIRouter()
router.include_router(router=auth_router)
router.include_router(router=jobs_router)
router.include_router(router=users_router)