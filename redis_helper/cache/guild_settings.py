from typing import Tuple, Optional, Dict
from aioredis import Redis
import msgpack


async def assign(redis: Redis, data):
    await redis.set(f"guild-settings-cache-{data['guild_id']}", msgpack.packb(data), expire=60)


async def delete(redis: Redis, guild_id: int):
    await redis.delete(f"guild-settings-cache-{guild_id}")


async def fetch(redis: Redis, guild_id: int) -> Tuple[bool, Optional[Dict]]:
    data = await redis.get(f"guild-settings-cache-{guild_id}", encoding=None)
    if data is None:
        return False, None
    return True, msgpack.unpackb(data)
