from aioredis import Redis
from ._helper import parse_emojis


async def assign(redis: Redis, guild_id: int, emojis):
    tr = redis.multi_exec()
    tr.delete(f"emojis-{guild_id}")
    if emojis:
        parse_emojis(tr, guild_id, emojis)
    await tr.execute()
