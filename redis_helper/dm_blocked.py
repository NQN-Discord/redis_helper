from typing import NoReturn
from aioredis import Redis


DM_BLOCK_TIME = 24 * 60 * 60


async def assign(redis: Redis, user_id: int) -> NoReturn:
    await redis.set(f"dm-blocked-{user_id}", "", expire=DM_BLOCK_TIME)


async def fetch(redis: Redis, user_id: int) -> bool:
    return await redis.exists(f"dm-blocked-{user_id}")
