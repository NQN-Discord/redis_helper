from typing import Dict, NoReturn, Optional, List
from aioredis import Redis
from time import time_ns
from itertools import repeat


ONE_DAY = 24 * 60 * 60


async def assign(redis: Redis, guild_id: int, emotes: Dict[str, str]) -> NoReturn:
    if emotes:
        tr = redis.pipeline()
        hash_key = f"emote-cache-{guild_id}"
        sorted_set_key = f"autocomplete-emojis-{guild_id}-recent"
        current_time = time_ns()
        tr.hmset_dict(hash_key, emotes)
        tr.zadd(sorted_set_key, *[x for xs in zip(repeat(current_time), (f"{emote_name.lower()}.{emote_str}" for emote_name, emote_str in emotes.items())) for x in xs])
        await tr.execute()
        tr = redis.pipeline()
        for key in emotes:
            _execute(tr, b"expiremember", hash_key, key, ONE_DAY)
            _execute(tr, b"expiremember", sorted_set_key, key, ONE_DAY)
        await tr.execute()


async def fetch(redis: Redis, guild_id: int, name: str) -> Optional[str]:
    return await redis.hget(f"emote-cache-{guild_id}", name)


async def fetch_all_by_score(redis: Redis, guild_id: int, prefix: str) -> List[str]:
    if prefix:
        emotes = await redis.zrevrangebyscore(f"autocomplete-emojis-{guild_id}-recent")
        emotes = (e for e in emotes if e.startswith(prefix))
    else:
        emotes = iter(await redis.zrevrangebyscore(f"autocomplete-emojis-{guild_id}-recent", offset=0, count=25))
    return [e.split(".", 1)[1] for e in emotes]


def _execute(redis, *args):
    return redis.__getattr__("execute")(*args)
