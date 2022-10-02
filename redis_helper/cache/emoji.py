from typing import List
from aioredis import Redis
from ._helper import parse_emojis
from ..assign_hashmap_keep_ttl import assign_hashmap_keep_ttl, execute_transaction
from ..protobuf.discord_pb2 import EmojiData
from google.protobuf.json_format import MessageToDict


async def assign(redis: Redis, guild_id: int, emojis):
    tr = redis.multi_exec()
    parse_emojis(assign_hashmap_keep_ttl(tr, guild_id), guild_id, emojis)
    await execute_transaction(tr, lambda: assign(redis, guild_id, emojis))


async def fetch_guilds(redis: Redis, guild_ids: List[int]):
    tr = redis.pipeline()
    guild_data = {}
    for guild_id in guild_ids:
        guild_data[guild_id] = tr.hgetall(f"emojis-{guild_id}", encoding=None)
    await tr.execute()
    return {k: load_emojis(await v) for k, v in guild_data.items()}


def load_emojis(d):
    return [MessageToDict(EmojiData.FromString(v), preserving_proto_field_name=True, use_integers_for_enums=True, including_default_value_fields=True) for v in d.values()]
