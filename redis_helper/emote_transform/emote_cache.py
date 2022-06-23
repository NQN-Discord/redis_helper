from typing import Dict, NoReturn, Optional
from aioredis import Redis
from time import time_ns
from itertools import repeat


ONE_DAY = 24 * 60 * 60


async def assign(redis: Redis, guild_id: int, emotes: Dict[str, str]) -> NoReturn:
    if emotes:
        tr = redis.pipeline()
        hash_key = f"emote-cache-{guild_id}"
        sorted_set_key = f"emote-cache-{guild_id}-lookup"
        current_time = time_ns()
        tr.hmset_dict(hash_key, emotes)
        tr.zadd(sorted_set_key, *[x for xs in zip(repeat(current_time), emotes.keys()) for x in xs])
        await tr.execute()
        tr = redis.pipeline()
        for key in emotes:
            tr.__getattr__("execute")(b"expiremember", hash_key, key, ONE_DAY)
            tr.__getattr__("execute")(b"expiremember", sorted_set_key, key, ONE_DAY)
        await tr.execute()


async def fetch(redis: Redis, guild_id: int, name: str) -> Optional[str]:
    return await redis.hget(f"emote-cache-{guild_id}", name)
