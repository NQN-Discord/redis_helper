from typing import Tuple
from aioredis import Redis
from collections import namedtuple
from itertools import cycle, chain
from asyncio import gather

EmojiTypes = namedtuple('EmojiTypes', ["current_server", "alias", "mutual_server", "pack"])

EXPIRE_TIME = 30


def _get_keys(user_id):
    return (
        f"autocomplete-emojis-{user_id}-guild",
        f"autocomplete-emojis-{user_id}-alias",
        f"autocomplete-emojis-{user_id}-mutual",
        f"autocomplete-emojis-{user_id}-pack",
    )


async def fetch(redis: Redis, user_id: int, start: str, limit: int) -> Tuple[bool, EmojiTypes]:
    tr = redis.multi_exec()
    exists = tr.exists(f"autocomplete-emojis-{user_id}")
    ranges = [tr.zrangebylex(key, min=start.encode("utf8"), offset=0, count=limit) for key in _get_keys(user_id)]
    await tr.execute()
    return (
        bool(await exists),
        EmojiTypes(*[[e.split(".", 1)[1] for e in l] for l in await gather(*ranges)])
    )


async def assign(redis: Redis, user_id: int, emoji_types: EmojiTypes):
    tr = redis.multi_exec()
    tr.set(f"autocomplete-emojis-{user_id}", 1, expire=EXPIRE_TIME)
    for key, emojis in zip(_get_keys(user_id), emoji_types):
        if emojis:
            tr.zadd(key, *chain(*zip(cycle([0]), (f"{emoji.name.lower()}.{emoji}" for emoji in emojis))))
            tr.expire(key, EXPIRE_TIME)
    await tr.execute()


async def reset_expire(redis: Redis, user_id: int):
    tr = redis.multi_exec()
    tr.set(f"autocomplete-emojis-{user_id}", 1, expire=EXPIRE_TIME)
    for key in _get_keys(user_id):
        tr.expire(key, EXPIRE_TIME)
    await tr.execute()
