from aioredis import Redis
from ._helper import parse_roles


async def assign(redis: Redis, guild_id: int, role):
    await parse_roles(redis.hmset_dict, guild_id, [role])


async def delete(redis: Redis, guild_id: int, role_id: int):
    await redis.hdel(f"roles-{guild_id}", role_id)
