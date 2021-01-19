from typing import Iterator, List
from itertools import chain
from aioredis import Redis
import msgpack
from ._helper import guild_keys, GUILD_ATTRS, parse_roles, parse_emojis, parse_channels


async def fetch_guild_ids(redis: Redis) -> List[int]:
    return [int(i) for i in await redis.smembers("guilds")]


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


async def fetch_guild_emojis_only(redis: Redis, guild_ids: List[int]):
    tr = redis.pipeline()
    futures = {}
    for guild_id in guild_ids:
        futures[guild_id] = {
            "emojis": tr.hgetall(f"emojis-{guild_id}", encoding=None)
        }
    await tr.execute()
    del tr

    for guild_id in guild_ids:
        yield {
            "emojis": _parse_id_dict(await futures[guild_id]["emojis"]),
            "id": guild_id
        }


async def fetch_guild(redis: Redis, guild_id: int, user=None):
    async for guild in fetch_guilds(redis, guild_ids=[guild_id], user=user, emojis=True):
        return guild


async def fetch_guilds(redis: Redis, guild_ids: List[int], user, emojis: bool = False):
    tr = redis.pipeline()
    attrs = {
        "channels": tr.hgetall,
        "roles": tr.hgetall,
        "guild": tr.hgetall,
        "me": tr.smembers,
        "nick": tr.get
    }
    if emojis:
        attrs["emojis"] = tr.hgetall
    futures = {}
    for guild_id in guild_ids:
        futures[guild_id] = {attr: f(f"{attr}-{guild_id}", encoding=None) for attr, f in attrs.items()}
    await tr.execute()
    del tr
    for guild_id in guild_ids:
        nick = await futures[guild_id]["nick"]
        guild = {
            "channels": _parse_id_dict(await futures[guild_id]["channels"]),
            "roles": _parse_id_dict(await futures[guild_id]["roles"]),
            "members": [{
                "user": user,
                "roles": [int(r) for r in await futures[guild_id]["me"]],
                "nick": None if nick is None else nick.decode("utf-8")
            }],
            "id": guild_id,
            **{k.decode("utf-8"): v.decode("utf-8") for k, v in (await futures[guild_id]["guild"]).items()},
        }
        if emojis:
            guild["emojis"] = _parse_id_dict(await futures[guild_id]["emojis"])
        for channel in guild["channels"]:
            channel.pop("topic", None)
        guild["member_count"] = int(guild.get("member_count", "0"))
        guild["system_channel_id"] = guild.get("system_channel_id") or None
        guild["premium_tier"] = int(guild.get("premium_tier", "0") or "0")
        guild["icon"] = guild.get("icon") or None
        try:
            guild["members"][0]["joined_at"] = guild["joined_at"]
        except KeyError:
            guild["members"][0]["joined_at"] = None
        yield guild


def _parse_id_dict(d):
    return [msgpack.unpackb(v) for v in d.values()]
