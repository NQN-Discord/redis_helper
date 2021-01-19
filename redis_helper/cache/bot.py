from aioredis import Redis
import msgpack


async def assign_me(redis: Redis, user):
    await redis.set("user", msgpack.packb(user))


async def fetch_me(redis: Redis):
    return msgpack.unpackb(await redis.get("user", encoding=None))


async def assign_member(redis: Redis, user):
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
