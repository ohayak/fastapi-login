from typing import Any, Generator

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine

from settings import settings

url = URL.create(
    drivername=settings.db_driver,
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

engine: Engine = create_engine(url)

async_engine: AsyncEngine = create_async_engine(url, future=True)


def gen_session(auto_commit=True) -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
        if auto_commit:
            session.commit()


async def gen_async_session(auto_commit=True) -> Generator[AsyncSession, Any, None]:
    with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session
        if auto_commit:
            session.commit()


def get_session() -> Session:
    return Session(engine)


async def get_async_session() -> AsyncSession:
    return AsyncSession(async_engine, expire_on_commit=False)
