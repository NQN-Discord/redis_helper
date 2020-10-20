from aioredis import Redis
from ._helper import parse_channels


async def assign(redis: Redis, guild_id: int, channel):
    await parse_channels(redis, guild_id, [channel])


async def delete(redis: Redis, guild_id: int, channel_id: int):
    await redis.hdel(f"channels-{guild_id}", channel_id)
