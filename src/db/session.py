from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.ASYNC_DB_AUTH_URI,
    echo=False,
    future=True,
    pool_size=POOL_SIZE,
    max_overflow=64,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class SessionLocalBySchema(AsyncSession):
    def __call__(schema: str = None) -> AsyncSession:
        search_path = f"{schema},public" if schema else "public"
        engine = create_async_engine(
            settings.ASYNC_DB_DATA_URI,
            echo=False,
            future=True,
            pool_size=POOL_SIZE,
            max_overflow=64,
            connect_args={"options": f"-csearch_path={search_path}"},
        )
        session = super().__call__(
            autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        return session
