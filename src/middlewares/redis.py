from contextvars import ContextVar
from typing import Optional

from redis.asyncio import Redis, from_url
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp


class ClientNotInitialisedError(Exception):
    """Exception raised when the user creates a new session without first initialising the engine."""

    def __init__(self):
        msg = """
        Engine not initialised! Ensure that ContextDatabaseMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


_client: ContextVar[Optional[Redis]] = ContextVar("_client", default=None)


def get_ctx_client() -> Redis:
    """Return an instance of Client local to the current async context."""

    client = _client.get()
    if client is None:
        raise ClientNotInitialisedError

    return client


class ContextRedisMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, url: str):
        super().__init__(app)
        client = from_url(
            url,
            max_connections=10,
            encoding="utf8",
            decode_responses=True,
        )
        _client.set(client)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        return await call_next(request)
