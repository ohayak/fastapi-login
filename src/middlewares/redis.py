from contextvars import ContextVar
from typing import Optional

from redis.asyncio import Redis, from_url
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp


class MissingClientError(Exception):
    pass


class RedisNotInitialisedError(Exception):
    """Exception raised when the user creates a new session without first initialising the engine."""

    def __init__(self):
        msg = """
        Engine not initialised! Ensure that ContextRedisMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


_redis: Optional[Redis] = None
_client: ContextVar[Optional[Redis]] = ContextVar("_client", default=None)


def get_ctx_client() -> Redis:
    """Return an instance of Client local to the current async context."""

    if _redis is None:
        raise RedisNotInitialisedError

    client = _client.get()
    if client is None:
        raise MissingClientError

    return client


class ContextClient:
    def __init__(self):
        self.token = None

    async def __aenter__(self):
        if _redis is None:
            raise RedisNotInitialisedError
        # get single connection client
        self.token = _client.set(_redis.client())
        return type(self)

    async def __aexit__(self, exc_type, exc_value, traceback):
        client = _client.get()
        await client.close(close_connection_pool=False)
        _client.reset(self.token)


class ContextRedisMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, url: str):
        super().__init__(app)
        redis = from_url(
            url,
            max_connections=10,
            encoding="utf8",
            decode_responses=True,
        )
        global _redis
        _redis = redis

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        async with ContextClient():
            return await call_next(request)
