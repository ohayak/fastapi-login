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

def gen_session(auto_commit=True) -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
            if auto_commit:
                session.commit()
        except:
            session.rollback()

async def gen_async_session(auto_commit=True) -> Generator[AsyncSession, None, None]:
    async with AsyncSession(async_engine) as session:
        try:
            yield session
            if auto_commit:
                await session.commit()
        except:
            await session.rollback()


def get_session() -> Session:
    return Session(engine)


async def get_async_session() -> AsyncSession:
    return AsyncSession(async_engine)
