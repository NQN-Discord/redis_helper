from aioredis import Redis
from uuid import uuid4


INTERACTION_CACHE_TIME = 3 * 60 * 60


async def assign(redis: Redis, custom_id: str) -> str:
    uuid = str(uuid4())
    await redis.set(f"interactions-{uuid}", custom_id, expire=INTERACTION_CACHE_TIME)
    return uuid


async def fetch(redis: Redis, custom_id: str) -> str:
    return await redis.get(f"interactions-{custom_id}")
