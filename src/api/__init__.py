from fastapi import APIRouter

from api.docs import router as docs
from api.v1 import api_router as api_v1
from core.settings import settings

router = APIRouter()

@router.get("/")
async def root():
    return {"message": f"Welcome to {settings.API_TITLE} {settings.API_VERSION} use /v1/redoc for documentation", "status": "success"}

router.include_router(docs)
router.include_router(api_v1, prefix="/v1")
