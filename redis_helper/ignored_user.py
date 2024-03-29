from typing import NoReturn, Tuple
from aioredis import Redis
try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

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


@asynccontextmanager
async def _ttl(redis, user):
    tr = redis.pipeline()
    count_ttl = tr.ttl(f"user-ratelimit-count-{user}")
    unique_ttl = tr.ttl(f"user-ratelimit-unique-{user}")
    yield tr
    await tr.execute()
    if await count_ttl <= 0:
        await redis.expire(f"user-ratelimit-count-{user}", RATELIMIT_TIME)
    if await unique_ttl <= 0:
        await redis.expire(f"user-ratelimit-unique-{user}", RATELIMIT_TIME)


async def total_and_unique_messages(redis: Redis, user: int, content: str) -> Tuple[int, int, bool]:
    async with _ttl(redis, user) as tr:
        total = tr.incr(f"user-ratelimit-count-{user}")
        is_unique = tr.sadd(f"user-ratelimit-unique-{user}", content)
        total_unique = tr.scard(f"user-ratelimit-unique-{user}")
    return await total, await total_unique, bool(await is_unique)


async def delete_user_message(redis: Redis, user: int, content: str):
    async with _ttl(redis, user) as tr:
        tr.decr(f"user-ratelimit-count-{user}")
        tr.srem(f"user-ratelimit-unique-{user}", content)


async def total_for_message(redis: Redis, content: str) -> int:
    tr = redis.pipeline()
    total = tr.incr(f"user-ratelimit-global-{content}")
    tr.expire(f"user-ratelimit-global-{content}", RATELIMIT_TIME)
    await tr.execute()
    return await total


async def can_send_spam_dm(redis: Redis, user: int) -> bool:
    can_send = await redis.set(f"user-ratelimit-dm-{user}", 0, expire=DM_SPAM_RATELIMIT, exist=redis.SET_IF_NOT_EXIST)
    return bool(can_send)
