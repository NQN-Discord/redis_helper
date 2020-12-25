from typing import Iterator
from aioredis import Redis


async def fetch_all_ids(redis: Redis) -> Iterator[int]:
    return map(int, await redis.smembers("pack-guild-ids"))


async def create(redis: Redis, guild_id: int):
    await redis.sadd("pack-guild-ids", guild_id)


async def delete(redis: Redis, *guild_ids: int):
    if not guild_ids:
        return
    await redis.srem("pack-guild-ids", *guild_ids)


async def exists(redis: Redis, guild_id: int):
    return await redis.sismember("pack-guild-ids", guild_id)
