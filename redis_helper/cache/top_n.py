from typing import NoReturn, List
from aioredis import Redis, ReplyError


TWO_WEEKS = 3600 * 24 * 14


async def initialise(redis: Redis, user_id: int) -> NoReturn:
    key = f"user-top-emojis-{user_id}"
    try:
        await redis.execute("TOPK.RESERVE", key, 25)
    except ReplyError as e:
        if e.args != ("TopK: key already exists",):
            raise
    await redis.expire(key, TWO_WEEKS)


async def add_emoji(redis: Redis, user_id: int, emoji_ids: List[int]) -> NoReturn:
    try:
        await redis.execute("TOPK.ADD", f"user-top-emojis-{user_id}", *emoji_ids)
    except ReplyError as e:
        if e.args != ("TopK: key does not exist",):
            raise


async def list_emojis(redis: Redis, user_id: int) -> List[int]:
    try:
        return [int(i) for i in await redis.execute("TOPK.LIST", f"user-top-emojis-{user_id}")]
    except ReplyError as e:
        if e.args != ("TopK: key does not exist",):
            raise
        return []
