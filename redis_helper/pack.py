from typing import Iterator
from aioredis import Redis

ONE_WEEK = 7 * 24 * 60 * 60


async def fetch_all_ids(redis: Redis) -> Iterator[int]:
    return map(int, await redis.smembers("pack-guild-ids"))


async def create(redis: Redis, guild_id: int):
    tr = redis.pipeline()
    tr.sadd("pack-guild-ids", guild_id)
    tr.set(f"pack-recent-{guild_id}", 0, expire=ONE_WEEK)
    await tr.execute()


async def delete(redis: Redis, *guild_ids: int):
    if not guild_ids:
        return
    await redis.srem("pack-guild-ids", *guild_ids)


async def exists(redis: Redis, guild_id: int):
    return bool(await redis.sismember("pack-guild-ids", guild_id))


async def created_recently(redis: Redis, guild_id: int) -> bool:
    return bool(await redis.exists(f"pack-recent-{guild_id}"))
