from aioredis import Redis


async def assign(redis: Redis, user_id: int, name: str, emoji: str, timeout: int):
    await redis.set(f"cached-user-emojis-{user_id}-{name}", emoji, expire=timeout)


async def expire(redis: Redis, user_id: int, name: str):
    await redis.delete(f"cached-user-emojis-{user_id}-{name}")


async def fetch(redis: Redis, user_id: int, name: str) -> str:
    return await redis.get(f"cached-user-emojis-{user_id}-{name}")
