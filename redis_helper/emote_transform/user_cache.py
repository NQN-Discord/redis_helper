from aioredis import Redis


def assign(redis: Redis, user_id: int, name: str, emoji: str, timeout: int):
    return redis.set(f"cached-user-emojis-{user_id}-{name}", emoji, expire=timeout)


def expire(redis: Redis, user_id: int, name: str):
    return redis.delete(f"cached-user-emojis-{user_id}-{name}")


def fetch(redis: Redis, user_id: int, name: str) -> str:
    return redis.get(f"cached-user-emojis-{user_id}-{name}")
