from datetime import timedelta
from uuid import UUID

from redis.asyncio import Redis

from middlewares.redis import get_ctx_client


def _gen_nonce_key(session_id: UUID) -> str:
    return f"session:{session_id}:nonce"


async def set_nonce(
    session_id: UUID,
    nonce: str,
    expire_time: timedelta,
    redis_client: Redis | None = None,
) -> str:
    redis_client = redis_client or get_ctx_client()
    nonce_key = _gen_nonce_key(session_id)
    await redis_client.set(nonce_key, nonce)
    await redis_client.expire(nonce_key, expire_time)
    return nonce_key


async def get_nonce(session_id: UUID, redis_client: Redis | None = None) -> str | None:
    redis_client = redis_client or get_ctx_client()
    nonce_key = _gen_nonce_key(session_id)
    valid_nonce = await redis_client.get(nonce_key)
    return valid_nonce


async def delete_nonce(session_id: UUID, redis_client: Redis | None = None):
    redis_client = redis_client or get_ctx_client()
    nonce_key = _gen_nonce_key(session_id)
    await redis_client.delete(nonce_key)
