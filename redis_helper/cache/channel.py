from aioredis import Redis
from ._helper import parse_channels, parse_thread, fetch_thread
from ..assign_hashmap_keep_ttl import assign_hashmap_keep_ttl, execute_transaction


async def assign(redis: Redis, guild_id: int, channel):
    tr = redis.multi_exec()
    parse_channels(assign_hashmap_keep_ttl(tr, guild_id, delete_key=False), guild_id, [channel])
    await execute_transaction(tr, lambda: assign(redis, guild_id, channel))


async def assign_thread(redis: Redis, guild_id: int, channel, expire: int):
    await parse_thread(redis, guild_id, channel, expire)


async def get_thread(redis: Redis, guild_id: int, thread_id: int):
    return await fetch_thread(redis, guild_id, thread_id)


async def delete(redis: Redis, guild_id: int, channel_id: int):
    await redis.hdel(f"channels-{guild_id}", channel_id)
