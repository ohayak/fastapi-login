from fastapi import APIRouter

from .auth import router as auth_router
from .jobs import router as jobs_router

api_router = APIRouter()

api_router.include_router(router=auth_router)
api_router.include_router(router=jobs_router)

