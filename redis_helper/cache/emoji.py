from aioredis import Redis
from ._helper import parse_emojis
from .guild import _parse_id_dict


async def assign(redis: Redis, guild_id: int, emojis):
    tr = redis.multi_exec()
    rtn = tr.hgetall(f"emojis-{guild_id}", encoding=None)
    tr.delete(f"emojis-{guild_id}")
    if emojis:
        parse_emojis(tr, guild_id, emojis)
    await tr.execute()
    return _parse_id_dict(await rtn)
