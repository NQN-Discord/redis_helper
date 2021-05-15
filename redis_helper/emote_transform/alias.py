from typing import Dict, NoReturn, List
from aioredis import Redis


async def assign(redis: Redis, user: int, name: str, value: str) -> NoReturn:
    tr = redis.pipeline()
    tr.hset(f"aliases-{user}", name, value)
    tr.sadd("aliases", user)
    await tr.execute()


async def fetch(redis: Redis, user: int, names: str) -> str:
    return await redis.hget(f"aliases-{user}", names)


async def fetch_multi(redis: Redis, user: int, names: List[str]) -> str:
    return await redis.hmget(f"aliases-{user}", *names)


async def list(redis: Redis, user: int) -> Dict[str, str]:
    return await redis.hgetall(f"aliases-{user}")


async def delete(redis: Redis, user: int, name: str) -> NoReturn:
    tr = redis.pipeline()
    tr.hdel(f"aliases-{user}", name)
    alias_count = tr.hlen(f"aliases-{user}")
    await tr.execute()
    alias_count = await alias_count
    if alias_count == 0:
        await redis.srem("aliases", user)


async def count(redis: Redis, user: int) -> int:
    return await redis.hlen(f"aliases-{user}")
