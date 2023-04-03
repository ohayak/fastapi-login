from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from utils.minio_client import Minio


class MissingBucketError(Exception):
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


class ClientNotInitialisedError(Exception):
    """Exception raised when the user creates a new session without first initialising the engine."""

    def __init__(self):
        msg = """
        Engine not initialised! Ensure that ContextDatabaseMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


_bucket: Optional[str] = None
_client: ContextVar[Optional[Minio]] = ContextVar("_client", default=None)


def get_ctx_session() -> Minio:
    """Return an instance of Session local to the current async context."""
    if _bucket is None:
        raise MissingBucketError

    client = _client.get()
    if client is None:
        raise ClientNotInitialisedError

    return client


class ContextMinioMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, minio_url: str, access_key: str, secret_key: str, bucket_name: str):
        super().__init__(app)
        self.minio_url = minio_url
        self.access_key = access_key
        self.secret_key = secret_key
        client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        global _bucket
        _bucket = bucket_name
        _client.set(client)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        return await call_next(request)
