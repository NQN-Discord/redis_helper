from aioredis import Redis
from ._helper import parse_roles
from ..assign_hashmap_keep_ttl import execute_transaction, assign_hashmap_keep_ttl


async def assign(redis: Redis, guild_id: int, role):
    tr = redis.multi_exec()
    parse_roles(assign_hashmap_keep_ttl(tr, guild_id, delete_key=False), guild_id, [role])
    await execute_transaction(tr, lambda: assign(redis, guild_id, role))


async def delete(redis: Redis, guild_id: int, role_id: int):
    await redis.hdel(f"roles-{guild_id}", role_id)
