from typing import Generator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session
from sqlalchemy.future import Engine

from settings import settings

import logging

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


async def gen_auth_async_session() -> Generator[AsyncSession, None, None]:
    async_session_factory = sessionmaker(auth_async_engine, expire_on_commit=False, class_= AsyncSession)
    async with async_scoped_session(async_session_factory) as session:
        try:
            yield session
            await session.commit()
        except:
            logging.error("something went wrong with SQL transaction, rolling back.")
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


async def gen_scheduler_async_session() -> Generator[AsyncSession, None, None]:
    async_session_factory = sessionmaker(scheduler_async_engine, expire_on_commit=False, class_= AsyncSession)
    async with async_scoped_session(async_session_factory) as session:
        try:
            yield session
            await session.commit()
        except:
            logging.error("something went wrong with SQL transaction, rolling back.")
            await session.rollback()


############
# Data
############


data_url = URL.create(
    drivername=settings.db_data_driver,
    username=settings.db_data_user,
    password=settings.db_data_password,
    host=settings.db_data_host,
    port=settings.db_data_port,
    database=settings.db_data_name,
)

data_async_engine: AsyncEngine = create_async_engine(data_url, future=True)


async def gen_data_async_session() -> Generator[AsyncSession, None, None]:
    async_session_factory = sessionmaker(data_async_engine, expire_on_commit=False, class_= AsyncSession)
    async with async_scoped_session(async_session_factory) as session:
        try:
            yield session
            await session.commit()
        except:
            logging.error("something went wrong with SQL transaction, rolling back.")
            await session.rollback()