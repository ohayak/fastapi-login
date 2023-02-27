from contextvars import ContextVar
from typing import Dict, Optional

from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
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
            await ctxdb.session.execute(foo.select()).fetchall()
        """

        super().__init__(msg)


class SessionNotInitialisedError(Exception):
    """Exception raised when the user creates a new DB session without first initialising it."""

    def __init__(self):
        msg = """
        Session not initialised! Ensure that DBSessionMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


_Session: Optional[sessionmaker] = None
_session: ContextVar[Optional[AsyncSession]] = ContextVar("_session", default=None)


class DBSessionMeta(type):
    # using this metaclass means that we can access ctxdb.session as a property at a class level,
    # rather than db().session
    @property
    def session(self) -> AsyncSession:
        """Return an instance of Session local to the current async context."""
        if _Session is None:
            raise SessionNotInitialisedError

        session = _session.get()
        if session is None:
            raise MissingSessionError

        return session


class DBSession(metaclass=DBSessionMeta):
    def __init__(self, session_args: Dict = None, commit_on_exit: bool = False):
        self.token = None
        self.session_args = session_args or {}
        self.commit_on_exit = commit_on_exit

    async def _init_session(self):
        self.token = _session.set(_Session(**self.session_args))  # type: ignore

    async def __aenter__(self):
        if not isinstance(_Session, sessionmaker):
            raise SessionNotInitialisedError

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


class ContextDBMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        custom_engine: Optional[Engine] = None,
        session_args: Dict = None,
        connect_args: Dict = None,
        commit_on_exit: bool = False,
    ):
        super().__init__(app)
        self.commit_on_exit = commit_on_exit
        session_args = session_args or {}
        connect_args = connect_args or {}

        if custom_engine:
            engine = custom_engine
        else:
            engine = create_async_engine(
                settings.ASYNC_DB_URI,
                echo=settings.DB_ECHO,
                pool_size=settings.POOL_SIZE,
                max_overflow=settings.MAX_OVERFLOW,
                connect_args=connect_args,
            )

        global _Session
        _Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, **session_args)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        async with DBSession(commit_on_exit=self.commit_on_exit):
            return await call_next(request)


ctxdb: DBSessionMeta = DBSession
