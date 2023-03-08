from datetime import timedelta
from typing import Optional, Set
from uuid import UUID

from redis.asyncio import Redis

from models.user_model import User
from schemas.common_schema import TokenType


def gen_token_key(user_id: UUID, token_type: str) -> str:
    return f"user:{user_id}:{token_type}"


async def add_token(
    redis_client: Redis,
    user_id: UUID,
    token: str,
    token_type: TokenType,
    expire_time: Optional[int] = None,
):
    token_key = gen_token_key(user_id, token_type)
    await redis_client.sadd(token_key, token)
    await redis_client.expire(token_key, timedelta(minutes=expire_time))


async def get_tokens(redis_client: Redis, user_id: UUID, token_type: TokenType) -> Set[str]:
    token_key = gen_token_key(user_id, token_type)
    valid_tokens = await redis_client.smembers(token_key)
    return valid_tokens


async def delete_tokens(redis_client: Redis, user_id: UUID, token_type: TokenType):
    token_key = gen_token_key(user_id, token_type)
    await redis_client.delete(token_key)
