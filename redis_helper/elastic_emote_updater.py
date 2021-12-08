from typing import List
from aioredis import Redis

REDIS_KEY = "elastic_emote_cache"


async def push(redis: Redis, payload: str):
    await redis.rpush(REDIS_KEY, payload)


async def fetch_all(redis: Redis) -> List[str]:
    tr = redis.multi_exec()
    data = tr.lrange(REDIS_KEY, 0, -1)
    tr.delete(REDIS_KEY)
    await tr.execute()
    return await data
