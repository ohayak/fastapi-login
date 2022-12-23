import hashlib
from typing import Optional

from starlette.requests import Request
from starlette.responses import Response


def default_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
):
    from fastapi_cache import FastAPICache

    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    cache_key = prefix + hashlib.md5(f"{func.__module__}:{func.__name__}:{args}:{kwargs}").hexdigest()  # nosec:B303
    return cache_key
