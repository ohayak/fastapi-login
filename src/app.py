import logging

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from redis import from_url
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api import router
from core.settings import settings
from middlewares.asql import ContextDatabaseMiddleware
from middlewares.redis import ContextRedisMiddleware

# Core Application Instance
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
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


@app.on_event("startup")
async def on_startup():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    redis_client = from_url(url=settings.REDIS_URL)
    try:
        redis_client.ping()
    except Exception:
        raise ConnectionRefusedError(f"Redis server not responding using {redis_client.get_connection_kwargs()}")
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    logging.info("startup fastapi")


# Add Apps
app.include_router(router)
add_pagination(app)
