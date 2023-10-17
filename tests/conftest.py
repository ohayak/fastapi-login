import warnings
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import ProgrammingError

import alembic.config
from core.security import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_engine() -> Engine:
    engine = create_engine(str(settings.DB_URL))
    return engine


def run_psql_without_transaction(command: str) -> None:
    engine = get_engine()
    connection = engine.connect()
    connection.connection.set_isolation_level(0)
    connection.execute(command)
    connection.connection.set_isolation_level(1)
    connection.close()


@pytest.fixture(scope="session")
def create_database() -> None:
    try:
        run_psql_without_transaction(f"CREATE DATABASE {settings.postgres_db}")
    except ProgrammingError:
        pass


def prepare_db() -> None:
    alembic.config.main(
        [
            "--raiseerr",
            "upgrade",
            "head",
        ]
    )


def drop_db() -> None:
    alembic.config.main(
        [
            "--raiseerr",
            "downgrade",
            "base",
        ]
    )


@pytest.fixture(scope="function")
def create_db(create_database: None) -> Generator[None, None, None]:
    prepare_db()
    yield
    drop_db()


@pytest.fixture(scope="function")
def app_fixture(create_db: None) -> TestClient:
    from main import app

    api_client = TestClient(app)

    return api_client


@pytest.fixture(scope="function")
def pg_conn() -> Generator[Connection, None, None]:
    engine = create_engine(str(settings.DB_URL), pool_size=0, echo=True)
    conn = engine.connect()

    yield conn

    conn.close()
