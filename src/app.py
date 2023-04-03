import logging

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.v1 import api_router as api_router_v1
from core.config import settings
from middlewares.asql import ContextDatabaseMiddleware
from middlewares.redis import ContextRedisMiddleware, get_ctx_session

# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(ContextDatabaseMiddleware, url=settings.ASYNC_DB_URL)
app.add_middleware(ContextRedisMiddleware, url=settings.REDIS_URL)


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
    redis_client = get_ctx_session()
    try:
        await redis_client.ping()
    except Exception:
        raise ConnectionRefusedError(f"Redis server not responding using {redis_client.get_connection_kwargs()}")
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    logging.info("startup fastapi")


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
add_pagination(app)
