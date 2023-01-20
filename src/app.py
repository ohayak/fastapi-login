import logging

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from api.deps import get_redis_client
from api.v1 import api_router as api_router_v1
from core.config import settings
from db.asqlalchemy import SQLAlchemyMiddleware
from utils.fastapi_cache import FastAPICache
from utils.fastapi_cache.backends.redis import RedisBackend

# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.ASYNC_DB_AUTH_URI,
    engine_args={
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": settings.POOL_SIZE,
        "max_overflow": 64,
    },
)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(self, http_code: int = None, code: str = None, message: str = None):
        self.http_code = http_code if http_code else 500
        self.code = code if code else str(self.http_code)
        self.message = message


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} {settings.API_V1_STR}"}


@app.on_event("startup")
async def on_startup():
    redis_client = await get_redis_client()

    try:
        await redis_client.ping()
    except Exception as e:
        logging.error("Redis server not responding")
        raise e

    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    logging.info("startup fastapi")


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
add_pagination(app)
