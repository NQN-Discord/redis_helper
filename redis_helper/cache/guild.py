from typing import Iterator, List
from itertools import chain, cycle
import time
from aioredis import Redis
from ..protobuf.discord_pb2 import RoleData, ChannelData
from ._helper import guild_keys, GUILD_ATTRS, parse_roles, parse_emojis, parse_channels
from google.protobuf.json_format import MessageToDict
from .emoji import load_emojis
from .bot import _assign_member, get_member

try:
    from prometheus_client import Histogram
except ImportError:
    prometheus_enabled = False
else:
    prometheus_enabled = True

    hour = 3600
    day = hour * 24
    last_read_time = Histogram(
        "guild_last_read_time",
        "When was the last time the bot last read the guild from the cache",
        namespace="nqn_common",
        buckets=[
            10, 60, 120, 300, 600, 1800,
            hour, 2 * hour, 6 * hour, 12 * hour,
            day, 2 * day, 3 * day, 7 * day,
            14 * day, 30 * day
        ]
    )


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


async def assign(redis: Redis, guild) -> bool:
    """
    Returns if the guild exists already
    """
    guild_id = guild["id"]
    tr = redis.multi_exec()
    guild_exists = tr.sismember("guilds", guild_id)
    tr.sadd("guilds", guild_id)
    guild_attrs = {k: guild.get(k) or "" for k in GUILD_ATTRS if k in guild}
    guild_attrs["features"] = int("COMMUNITY" in guild.get("features", []))
    tr.hmset_dict(f"guild-{guild_id}", guild_attrs)
    if "channels" in guild:
        tr.delete(f"roles-{guild_id}" f"channels-{guild_id}")
        parse_channels(tr, guild_id, guild["channels"])
    else:
        tr.delete(f"roles-{guild_id}")
    if "members" in guild and guild["members"]:
        # Doesn't happen on guild updates, but does on guild creates for both startup and joining a guild.
        member = guild["members"][0]
        _assign_member(tr, guild_id, member)
    parse_roles(tr, guild_id, guild["roles"])

    tr.delete(f"emojis-{guild_id}")
    parse_emojis(tr, guild_id, guild["emojis"])

    await tr.execute()
    exists = bool(await guild_exists)
    if not exists:
        if not ("members" in guild and guild["members"]):
            raise AssertionError(guild)
    return exists


async def fetch_guild(redis: Redis, guild_id: int, user=None):
    async for guild in fetch_guilds(redis, guild_ids=[guild_id], user=user, emojis=True):
        return guild


async def fetch_guilds(redis: Redis, guild_ids: List[int], user, emojis: bool = False):
    tr = redis.pipeline()
    _do_score_metric(tr, guild_ids)
    attrs = {
        "channels": tr.hgetall,
        "roles": tr.hgetall,
        "guild": tr.hgetall,
        "mem": tr.get
    }
    if emojis:
        attrs["emojis"] = tr.hgetall
    futures = {}
    for guild_id in guild_ids:
        futures[guild_id] = {attr: f(f"{attr}-{guild_id}", encoding=None) for attr, f in attrs.items()}
    await tr.execute()
    del tr
    for guild_id in guild_ids:
        guild = {
            "channels": load_channels(await futures[guild_id]["channels"]),
            "roles": load_roles(await futures[guild_id]["roles"]),
            "members": [{
                "user": user,
                **get_member(await futures[guild_id]["mem"])
            }],
            "id": guild_id,
            **{k.decode("utf-8"): v.decode("utf-8") for k, v in (await futures[guild_id]["guild"]).items()},
        }
        if emojis:
            guild["emojis"] = load_emojis(await futures[guild_id]["emojis"])
        for channel in guild["channels"]:
            channel.pop("topic", None)
        guild["member_count"] = 0
        guild["system_channel_id"] = None
        guild["premium_tier"] = int(guild.get("premium_tier", "0") or "0")
        guild["icon"] = guild.get("icon") or None
        guild["features"] = ["COMMUNITY"] if guild.get("features") == "1" else []
        try:
            guild["members"][0]["joined_at"] = guild["joined_at"]
        except KeyError:
            guild["members"][0]["joined_at"] = None
        yield guild


def load_roles(d):
    roles = [MessageToDict(RoleData.FromString(v), preserving_proto_field_name=True, use_integers_for_enums=True, including_default_value_fields=True) for v in d.values()]
    for r in roles:
        bot_id = r.pop("bot_id", None)
        if bot_id and bot_id != "0":
            r["tags"] = {"bot_id": bot_id}
    return roles


def load_channels(d):
    return [MessageToDict(ChannelData.FromString(v), preserving_proto_field_name=True, use_integers_for_enums=True, including_default_value_fields=True) for v in d.values()]


def _do_score_metric(tr: Redis, guild_ids: List[int]):
    def inner(future):
        results = [(current_time - float(i)) / 10**9 for i in future.result() if i is not None]
        for i in results:
            last_read_time.observe(i)

    current_time = time.time_ns()
    if prometheus_enabled:
        _execute(tr, "zmscore", "guild_last_read", *guild_ids).add_done_callback(inner)
    tr.zadd("guild_last_read", *chain(*zip(cycle([current_time]), guild_ids)))


def _execute(redis, *args):
    return redis.__getattr__("execute")(*args)
