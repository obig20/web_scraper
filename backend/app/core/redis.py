"""Redis client for caching and rate limiting."""

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Any | None:
    client = await get_redis()
    value = await client.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    client = await get_redis()
    serialized = json.dumps(value) if not isinstance(value, str) else value
    await client.setex(key, ttl, serialized)


async def cache_delete(key: str) -> None:
    client = await get_redis()
    await client.delete(key)
