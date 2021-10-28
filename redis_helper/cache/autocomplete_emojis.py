from typing import Tuple
from aioredis import Redis
from collections import namedtuple
from itertools import cycle, chain
from asyncio import gather
from enum import Flag, auto

EmojiTypes = namedtuple('EmojiTypes', ["current_server", "alias", "mutual_server", "pack"])


class EmojiSource(Flag):
    CURRENT_SERVER = auto()
    ALIAS = auto()
    MUTUAL_SERVER = auto()
    PACK = auto()


ALL = EmojiSource.CURRENT_SERVER | EmojiSource.ALIAS | EmojiSource.MUTUAL_SERVER | EmojiSource.PACK


EXPIRE_TIME = 30


def _get_keys(user_id, sources: EmojiSource):
    return [
        (sources.CURRENT_SERVER, f"autocomplete-emojis-{user_id}-guild"),
        (sources.ALIAS, f"autocomplete-emojis-{user_id}-alias"),
        (sources.MUTUAL_SERVER, f"autocomplete-emojis-{user_id}-mutual"),
        (sources.PACK, f"autocomplete-emojis-{user_id}-pack"),
    ]


async def _none():
    return []


async def fetch(redis: Redis, user_id: int, sources: EmojiSource, start: str, limit: int) -> Tuple[bool, EmojiTypes]:
    tr = redis.multi_exec()
    exists = tr.exists(f"autocomplete-emojis-{user_id}")
    ranges = [
        tr.zrangebylex(key, min=start.encode("utf8"), offset=0, count=limit) if sources & source else _none()
        for source, key in _get_keys(user_id, sources)
    ]
    await tr.execute()
    return (
        bool(EmojiSource(await exists) & sources),
        EmojiTypes(*[[e.split(".", 1)[1] for e in l] for l in await gather(*ranges)])
    )


async def assign(redis: Redis, user_id: int, emoji_types: EmojiTypes, sources: EmojiSource):
    tr = redis.multi_exec()
    tr.set(f"autocomplete-emojis-{user_id}", sources.value, expire=EXPIRE_TIME)
    for (source, key), emojis in zip(_get_keys(user_id, sources), emoji_types):
        if emojis and sources & source:
            tr.zadd(key, *chain(*zip(cycle([0]), (f"{emoji.name.lower()}.{emoji}" for emoji in emojis))))
            tr.expire(key, EXPIRE_TIME)
    await tr.execute()


async def reset_expire(redis: Redis, user_id: int):
    tr = redis.multi_exec()
    tr.expire(f"autocomplete-emojis-{user_id}", expire=EXPIRE_TIME)
    for _, key in _get_keys(user_id, ALL):
        tr.expire(key, EXPIRE_TIME)
    await tr.execute()
