from typing import Dict, NoReturn, Optional
from aioredis import Redis


ONE_DAY = 24 * 60 * 60


async def assign(redis: Redis, guild_id: int, emotes: Dict[str, str]) -> NoReturn:
    if emotes:
        tr = redis.pipeline()
        for name, emote in emotes.items():
            tr.set(f"emote_transform_emote_cache_{guild_id}_{name}", emote, expire=ONE_DAY)
        await tr.execute()


async def fetch(redis: Redis, guild_id: int, name: str) -> Optional[str]:
    return await redis.get(f"emote_transform_emote_cache_{guild_id}_{name}")
