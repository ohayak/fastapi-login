from datetime import timedelta
from enum import Enum
from typing import Set
from uuid import UUID

from redis.asyncio import Redis

from middlewares.redis import get_ctx_client


class TokenType(str, Enum):
    JWT = "jwt"


def _gen_token_key(user_id: UUID, token_type: str) -> str:
    return f"user:{user_id}:{token_type}"


async def set_token(
    user_id: UUID,
    token: str,
    token_type: TokenType,
    expire_time: timedelta,
    redis_client: Redis | None = None,
) -> str:
    redis_client = redis_client or get_ctx_client()
    token_key = _gen_token_key(user_id, token_type)
    await redis_client.sadd(token_key, token)
    await redis_client.expire(token_key, expire_time)
    return token_key


async def get_tokens(
    user_id: UUID,
    token_type: TokenType,
    redis_client: Redis | None = None,
) -> Set[str]:
    redis_client = redis_client or get_ctx_client()
    token_key = _gen_token_key(user_id, token_type)
    valid_tokens = await redis_client.smembers(token_key)
    return valid_tokens


async def delete_tokens(
    user_id: UUID,
    token_type: TokenType,
    redis_client: Redis | None = None,
):
    redis_client = redis_client or get_ctx_client()
    token_key = _gen_token_key(user_id, token_type)
    await redis_client.delete(token_key)
