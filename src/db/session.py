from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config import settings


def session_by_schema(schema: str = None) -> AsyncSession:
    search_path = f"{schema},public" if schema else "public"
    session = AsyncSession(
        bind=create_async_engine(
            settings.ASYNC_DB_URI,
            echo=settings.DB_ECHO,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
            connect_args={"server_settings": {"search_path": search_path}},
        ),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    return session
