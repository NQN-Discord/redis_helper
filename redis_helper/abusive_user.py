from typing import NoReturn
from aioredis import Redis


async def count(redis: Redis) -> int:
    return await redis.scard("message-repost-abusive-users")


async def exists(redis: Redis, user: int) -> bool:
    return await redis.sismember("message-repost-abusive-users", user)


async def create(redis: Redis, user: int, *users: int) -> NoReturn:
    await redis.sadd("message-repost-abusive-users", user, *users)


async def delete(redis: Redis, user: int) -> NoReturn:
    await redis.srem("message-repost-abusive-users", user)

