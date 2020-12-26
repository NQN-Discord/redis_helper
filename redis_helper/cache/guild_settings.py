from typing import Tuple, Optional, Dict
from aioredis import Redis
import json


async def assign(redis: Redis, data):
    await redis.set(f"guild-settings-cache-{data['guild_id']}", json.dumps(data), expire=5)


async def delete(redis: Redis, guild_id: int):
    await redis.delete(f"guild-settings-cache-{guild_id}")


async def fetch(redis: Redis, guild_id: int) -> Tuple[bool, Optional[Dict]]:
    data = await redis.get(f"guild-settings-cache-{guild_id}")
    if data is None:
        return False, None
    return True, json.loads(data)
