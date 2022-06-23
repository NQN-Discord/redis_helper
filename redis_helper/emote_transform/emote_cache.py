from typing import Dict, NoReturn, Optional
from aioredis import Redis


ONE_DAY = 24 * 60 * 60


async def assign(redis: Redis, guild_id: int, emotes: Dict[str, str]) -> NoReturn:
    if emotes:
        tr = redis.pipeline()
        hash_key = f"emote-cache-{guild_id}"
        tr.hmset_dict(hash_key, emotes)
        for key in emotes:
            tr.__getattr__("execute")(b"expiremember", hash_key, key, ONE_DAY)
        await tr.execute()


async def fetch(redis: Redis, guild_id: int, name: str) -> Optional[str]:
    return await redis.hget(f"emote-cache-{guild_id}", name)
