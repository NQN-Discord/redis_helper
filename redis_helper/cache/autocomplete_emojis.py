import asyncio
from typing import Tuple, Optional, List
from aioredis import Redis
from itertools import cycle, chain
from asyncio import gather
from enum import Flag, auto
from dataclasses import dataclass, field, fields


@dataclass
class EmojiTypes:
    current_server: List[str]
    alias: List[str]
    mutual_server: List[str]
    pack: List[str]
    # Optional for non-guild usages
    server_alias: List[str] = field(default_factory=list)
    server_pack: List[str] = field(default_factory=list)
    server_recently_used: List[str] = field(default_factory=list)

    def items(self):
        for field in _field_names:
            yield field, getattr(self, field)


class EmojiSource(Flag):
    CURRENT_SERVER = auto()
    ALIAS = auto()
    MUTUAL_SERVER = auto()
    PACK = auto()
    SERVER_ALIAS = auto()
    SERVER_PACK = auto()
    SERVER_RECENTLY_USED = auto()


ALL = EmojiSource.CURRENT_SERVER | EmojiSource.ALIAS | EmojiSource.MUTUAL_SERVER | EmojiSource.PACK | EmojiSource.SERVER_ALIAS | EmojiSource.SERVER_PACK | EmojiSource.SERVER_RECENTLY_USED
CURRENT_SERVER_EXPLICIT = EmojiSource.CURRENT_SERVER | EmojiSource.SERVER_ALIAS | EmojiSource.SERVER_PACK


EXPIRE_TIME = 30
_field_names = [field.name for field in fields(EmojiTypes)]


def _get_keys(user_id: int, guild_id: Optional[int], sources: EmojiSource) -> List[Tuple[EmojiSource, str]]:
    user_ids = [
        (sources.CURRENT_SERVER, f"autocomplete-emojis-{user_id}-guild"),
        (sources.ALIAS, f"autocomplete-emojis-{user_id}-alias"),
        (sources.MUTUAL_SERVER, f"autocomplete-emojis-{user_id}-mutual"),
        (sources.PACK, f"autocomplete-emojis-{user_id}-pack"),
    ]
    guild_ids = []
    if guild_id:
        guild_ids = [
            (sources.SERVER_ALIAS, f"autocomplete-emojis-{guild_id}-alias"),
            (sources.SERVER_PACK, f"autocomplete-emojis-{guild_id}-pack"),
        ]
    return [*user_ids, *guild_ids]


async def _none():
    return []


async def fetch(redis: Redis, user_id: int, guild_id: Optional[int], sources: EmojiSource, start: str, limit: int) -> Tuple[EmojiSource, EmojiTypes]:
    tr = redis.multi_exec()
    exists = tr.get(f"autocomplete-emojis-{user_id}")
    encoded_prefix = start.lower().encode("utf8")
    ranges = [
        tr.zrangebylex(key, min=encoded_prefix, offset=0, count=limit) if sources & source else _none()
        for source, key in _get_keys(user_id, guild_id, sources)
    ]
    await tr.execute()
    exists = await exists
    autocomplete_ranges = await gather(*ranges)
    return (
        EmojiSource(0 if exists is None else int(exists)) & sources,
        EmojiTypes(*[[e.split(".", 1)[1] for e in l] for l in autocomplete_ranges])
    )


async def assign(redis: Redis, user_id: int, guild_id: Optional[int], emoji_types: EmojiTypes, sources: EmojiSource):
    tr = redis.multi_exec()
    tr.set(f"autocomplete-emojis-{user_id}", sources.value, expire=EXPIRE_TIME)
    for (source, key), emojis in zip(_get_keys(user_id, guild_id, sources), _get_values(emoji_types)):
        if emojis and sources & source:
            tr.zadd(key, *chain(*zip(cycle([0]), (f"{emoji.name.lower()}.{emoji}" for emoji in emojis))))
            tr.expire(key, EXPIRE_TIME)
    await tr.execute()


async def reset_expire(redis: Redis, user_id: int, guild_id: Optional[int]):
    tr = redis.multi_exec()
    tr.expire(f"autocomplete-emojis-{user_id}", EXPIRE_TIME)
    for _, key in _get_keys(user_id, guild_id, ALL):
        tr.expire(key, EXPIRE_TIME)
    await tr.execute()


def _get_values(emoji_types: EmojiTypes):
    return (getattr(emoji_types, field) for field in _field_names)
