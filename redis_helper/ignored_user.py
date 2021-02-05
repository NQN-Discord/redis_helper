from typing import NoReturn, Tuple
from aioredis import Redis

DM_SPAM_RATELIMIT = 24 * 60 * 60
RATELIMIT_TIME = 5 * 60


async def count(redis: Redis) -> int:
    return await redis.scard("message-repost-ignored-users")


async def exists(redis: Redis, user: int) -> bool:
    return await redis.sismember("message-repost-ignored-users", user)


async def create(redis: Redis, user: int) -> NoReturn:
    await redis.sadd("message-repost-ignored-users", user)


async def delete(redis: Redis, user: int) -> NoReturn:
    await redis.srem("message-repost-ignored-users", user)


async def total_and_unique_messages(redis: Redis, user: int, content: str) -> Tuple[int, int, bool]:
    tr = redis.pipeline()
    is_new = tr.set(f"user-ratelimit-count-{user}", 0, expire=RATELIMIT_TIME, exist=redis.SET_IF_NOT_EXIST)
    total = tr.incr(f"user-ratelimit-count-{user}")
    is_unique = tr.sadd(f"user-ratelimit-unique-{user}", content)
    total_unique = tr.scard(f"user-ratelimit-unique-{user}")
    await tr.execute()
    if await is_new:
        await redis.expire(f"user-ratelimit-unique-{user}", RATELIMIT_TIME)
    return await total, await total_unique, bool(await is_unique)


async def can_send_spam_dm(redis: Redis, user: int) -> bool:
    can_send = await redis.set(f"user-ratelimit-dm-{user}", 0, expire=RATELIMIT_TIME, exist=redis.SET_IF_NOT_EXIST)
    return bool(can_send)