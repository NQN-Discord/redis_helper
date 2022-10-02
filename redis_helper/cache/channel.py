from aioredis import Redis
from ._helper import parse_channels, parse_thread, fetch_thread


async def assign(redis: Redis, guild_id: int, channel):
    await parse_channels(redis.hmset_dict, guild_id, [channel])


async def assign_thread(redis: Redis, guild_id: int, channel, expire: int):
    await parse_thread(redis, guild_id, channel, expire)


async def get_thread(redis: Redis, guild_id: int, thread_id: int):
    return await fetch_thread(redis, guild_id, thread_id)


async def delete(redis: Redis, guild_id: int, channel_id: int):
    await redis.hdel(f"channels-{guild_id}", channel_id)
