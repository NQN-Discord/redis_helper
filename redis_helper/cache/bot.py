from aioredis import Redis
from ._helper import parse_emojis


async def assign(redis: Redis, user):
    roles = user["roles"]
    guild_id = user["guild_id"]

    tr = redis.multi_exec()
    tr.delete(f"me-{guild_id}")
    if roles:
        tr.sadd(f"me-{guild_id}", *roles)

    if user.get("nick"):
        tr.set(f"nick-{guild_id}", user["nick"])
    else:
        tr.delete(f"nick-{guild_id}")
    await tr.execute()
