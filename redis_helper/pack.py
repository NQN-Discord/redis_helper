from typing import List, Tuple
from aioredis import Redis

ONE_WEEK = 7 * 24 * 60 * 60
ONE_MINUTE = 60


async def create(redis: Redis, guild_id: int, name: str):
    tr = redis.multi_exec()
    tr.zadd("pack-guild-names", 0, name)
    tr.set(f"pack-recent-{guild_id}", 0, expire=ONE_WEEK)
    await tr.execute()


async def delete(redis: Redis, name: str):
    await redis.zrem("pack-guild-names", name)


async def fetch_autocomplete(redis: Redis, start: str, limit: int) -> List[str]:
    return await redis.zrangebylex("pack-guild-names", min=start.encode("utf8"), offset=0, count=limit)


async def assign_user_packs_autocomplete(redis: Redis, user_id: int, packs: List[str]):
    tr = redis.multi_exec()
    for pack in packs:
        tr.zadd(f"pack-guild-names-{user_id}", 0, pack)
    tr.expire(f"pack-guild-names-{user_id}", ONE_MINUTE)
    await tr.execute()


async def fetch_user_packs_autocomplete(redis: Redis, user_id: int, start: str, limit: int) -> Tuple[List[str], bool]:
    tr = redis.multi_exec()
    packs = tr.zrangebylex(f"pack-guild-names-{user_id}", min=start.encode("utf8"), offset=0, count=limit)
    exists = tr.exists(f"pack-guild-names-{user_id}")
    await tr.execute()
    return await packs, bool(await exists)


async def delete_user_pack_autocomplete(redis: Redis, user_id: int, pack: str):
    await redis.zrem(f"pack-guild-names-{user_id}", pack)


async def created_recently(redis: Redis, guild_id: int) -> bool:
    return bool(await redis.exists(f"pack-recent-{guild_id}"))
