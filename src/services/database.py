from typing import Generator

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine

from settings import settings

#######
# Auth
#######

auth_url = URL.create(
    drivername=settings.db_auth_driver,
    username=settings.db_auth_user,
    password=settings.db_auth_password,
    host=settings.db_auth_host,
    port=settings.db_auth_port,
    database=settings.db_auth_name,
)

auth_async_engine: AsyncEngine = create_async_engine(auth_url, future=True)


async def gen_auth_async_session(auto_commit=True) -> Generator[AsyncSession, None, None]:
    async with AsyncSession(auth_async_engine) as session:
        try:
            yield session
            if auto_commit:
                await session.commit()
        except:
            await session.rollback()


############
# Scheduler
############


scheduler_url = URL.create(
    drivername=settings.db_scheduler_driver,
    username=settings.db_scheduler_user,
    password=settings.db_scheduler_password,
    host=settings.db_scheduler_host,
    port=settings.db_scheduler_port,
    database=settings.db_scheduler_name,
)

scheduler_async_engine: AsyncEngine = create_async_engine(scheduler_url, future=True)


async def gen_scheduler_async_session(auto_commit=True) -> Generator[AsyncSession, None, None]:
    async with AsyncSession(scheduler_async_engine) as session:
        try:
            yield session
            if auto_commit:
                await session.commit()
        except:
            await session.rollback()
