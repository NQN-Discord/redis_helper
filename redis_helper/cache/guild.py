from typing import Iterator
from itertools import chain
from aioredis import Redis
from ._helper import guild_keys, GUILD_ATTRS, parse_roles, parse_emojis, parse_channels


async def intersect_shard(redis: Redis, shard_id: int, no_shards: int, keep: Iterator[int]):
    shard_guilds = {int(i) for i in await redis.smembers("guilds") if (int(i) >> 22) % no_shards == shard_id}
    deleted = shard_guilds - set(keep)

    if deleted:
        tr = redis.multi_exec()
        tr.delete(*chain(*map(guild_keys, deleted)))
        tr.srem("guilds", *deleted)
        await tr.execute()


async def delete(redis: Redis, guild_id: int):
    tr = redis.multi_exec()
    tr.delete(*guild_keys(guild_id))
    tr.srem("guilds", guild_id)
    await tr.execute()


async def assign(redis: Redis, guild):
    guild_id = guild["id"]
    tr = redis.multi_exec()
    tr.sadd("guilds", guild_id)
    guild_attrs = {k: guild.get(k) or "" for k in GUILD_ATTRS if k in guild}
    if "system_channel_id" not in guild:
        guild_attrs["system_channel_id"] = ""
    tr.hmset_dict(f"guild-{guild_id}", guild_attrs)
    if "channels" in guild:
        tr.delete(f"roles-{guild_id}", f"role-perms-{guild_id}", f"channels-{guild_id}")
        parse_channels(tr, guild_id, guild["channels"])
    else:
        tr.delete(f"roles-{guild_id}", f"role-perms-{guild_id}")
    if "members" in guild and guild["members"]:
        member = guild["members"][0]
        roles = member["roles"]
        tr.delete(f"me-{guild_id}")
        if roles:
            tr.sadd(f"me-{guild_id}", *roles)
        if member.get("nick"):
            tr.set(f"nick-{guild_id}", member["nick"])
        else:
            tr.delete(f"nick-{guild_id}")
    parse_roles(tr, guild_id, guild["roles"])

    tr.delete(f"emojis-{guild_id}")
    parse_emojis(tr, guild_id, guild["emojis"])

    await tr.execute()

