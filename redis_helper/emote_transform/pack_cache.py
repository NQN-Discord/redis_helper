from typing import List, NoReturn, Optional
from aioredis import Redis


ONE_DAY = 24 * 60 * 60


async def assign(redis: Redis, guild_id: int, emotes: List[str], pack_id: int) -> NoReturn:
    if emotes:
        tr = redis.pipeline()
        for emote in emotes:
            tr.set(f"emote_transform_pack_cache_{guild_id}_{emote}", pack_id, expire=ONE_DAY)
        await tr.execute()


async def fetch(redis: Redis, guild_id: int, name: str) -> Optional[int]:
    result = await redis.get(f"emote_transform_pack_cache_{guild_id}_{name}")
    if result is not None:
        return int(result)
