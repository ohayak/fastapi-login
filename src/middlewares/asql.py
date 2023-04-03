from contextvars import ContextVar
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from core.config import settings


class MissingSessionError(Exception):
    """Excetion raised for when the user tries to access a database session before it is created."""

    def __init__(self):
        msg = """
        No session found! Either you are not currently in a request context,
        or you need to manually create a session context by using a `db` instance as
        a context manager e.g.:

        async with db():
            await get_ctx_sql().execute(foo.select()).fetchall()
        """

        super().__init__(msg)


class EngineNotInitialisedError(Exception):
    """Exception raised when the user creates a new session without first initialising the engine."""

    def __init__(self):
        msg = """
        Engine not initialised! Ensure that ContextDatabaseMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


_engine: Optional[AsyncEngine] = None
_session: ContextVar[Optional[AsyncSession]] = ContextVar("_session", default=None)


def get_ctx_session() -> AsyncSession:
    """Return an instance of Session local to the current async context."""
    if _engine is None:
        raise EngineNotInitialisedError

    session = _session.get()
    if session is None:
        raise MissingSessionError

    return session


def create_engine(url: str, schema: str = None) -> AsyncEngine:
    search_path = f"{schema},public" if schema else "public"
    engine = create_async_engine(
        url,
        echo=settings.DB_ECHO,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        connect_args={"server_settings": {"search_path": search_path}},
    )
    return engine


def create_session(url: str = None, schema: str = None, engine: AsyncEngine = None) -> AsyncSession:
    session = AsyncSession(
        bind=engine or create_engine(url, schema),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    return session


class ContextDatabase:
    def __init__(self, session_args: Dict = None, commit_on_exit: bool = False):
        self.token = None
        self.session_args = session_args or {}
        self.commit_on_exit = commit_on_exit

    async def _init_session(self):
        self.token = _session.set(create_session(engine=_engine, **self.session_args))  # type: ignore

    async def __aenter__(self):
        if _engine is None:
            raise EngineNotInitialisedError

        await self._init_session()
        return type(self)

    async def __aexit__(self, exc_type, exc_value, traceback):
        session = _session.get()
        if exc_type is not None:
            await session.rollback()

        if self.commit_on_exit:
            await session.commit()

        await session.close()
        _session.reset(self.token)


class ContextDatabaseMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        url: str,
        schema: str = None,
        commit_on_exit: bool = False,
    ):
        super().__init__(app)
        self.commit_on_exit = commit_on_exit
        global _engine
        _engine = create_engine(url, schema)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        async with ContextDatabase(commit_on_exit=self.commit_on_exit):
            return await call_next(request)
