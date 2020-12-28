from typing import NoReturn
from aioredis import Redis


async def count(redis: Redis) -> int:
    return await redis.scard("message-repost-ignored-users")


async def exists(redis: Redis, user: int) -> bool:
    return await redis.sismember("message-repost-ignored-users", user)


async def create(redis: Redis, user: int) -> NoReturn:
    await redis.sadd("message-repost-ignored-users", user)


async def delete(redis: Redis, user: int) -> NoReturn:
    await redis.srem("message-repost-ignored-users", user)
