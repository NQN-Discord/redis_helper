from typing import List, Optional, NoReturn
from aioredis import Redis


async def assign_hash_ids(redis: Redis, emote_hash: str, ids: List[str], times_used: Optional[int]) -> NoReturn:
    if ids:
        tr = redis.pipeline()
        for id in ids:
            tr.set(f"extra-emote-id-hashes-{id}", emote_hash)

        if times_used is not None:
            tr.set(f"extra-emote-times-used-{emote_hash}", times_used)
        tr.sadd(f"extra-emote-updates", emote_hash)
        await tr.execute()


async def delete(redis: Redis, emote_hash: str, ids: List[str]) -> NoReturn:
    tr = redis.pipeline()
    for id in ids:
        tr.delete(f"extra-emote-id-hashes-{id}")
    tr.delete(f"extra-emote-times-used-{emote_hash}")
    tr.srem(f"extra-emote-updates", emote_hash)
    await tr.execute()


async def fetch_emote_hash(redis: Redis, emote_id: int) -> Optional[str]:
    return await redis.get(f"extra-emote-id-hashes-{emote_id}")


async def assign_emote_hash(self, emote_id: int, emote_hash: str) -> NoReturn:
    await self.redis.set(f"extra-emote-id-hashes-{emote_id}", emote_hash)


async def increment_ids(redis: Redis, emote_ids: List[str]) -> NoReturn:
    tr = redis.pipeline()
    for id in emote_ids:
        tr.get(f"extra-emote-id-hashes-{id}")
    hashes = set(await tr.execute()) - {None}
    if hashes:
        tr = redis.pipeline()
        for emote_hash in hashes:
            tr.incr(f"extra-emote-times-used-{emote_hash}")
        await tr.execute()
