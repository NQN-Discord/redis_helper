from aioredis import Redis

ONE_WEEK = 7 * 24 * 60 * 60


async def create(redis: Redis, guild_id: int, name: str):
    tr = redis.multi_exec()
    tr.zadd("pack-guild-names", 0, name)
    tr.set(f"pack-recent-{guild_id}", 0, expire=ONE_WEEK)
    await tr.execute()


async def delete(redis: Redis, name: str):
    await redis.zrem("pack-guild-names", name)


async def created_recently(redis: Redis, guild_id: int) -> bool:
    return bool(await redis.exists(f"pack-recent-{guild_id}"))
