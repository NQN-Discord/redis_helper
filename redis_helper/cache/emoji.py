from typing import List
from aioredis import Redis
from ._helper import parse_emojis
from ..protobuf.discord_pb2 import EmojiData
from google.protobuf.json_format import MessageToDict


async def assign(redis: Redis, guild_id: int, emojis):
    tr = redis.multi_exec()
    rtn = tr.hgetall(f"emojis-{guild_id}", encoding=None)
    tr.delete(f"emojis-{guild_id}")
    if emojis:
        parse_emojis(tr, guild_id, emojis)
    await tr.execute()
    return load_emojis(await rtn)


async def fetch_guilds(redis: Redis, guild_ids: List[int]):
    tr = redis.pipeline()
    guild_data = {}
    for guild_id in guild_ids:
        guild_data[guild_id] = tr.hgetall(f"emojis-{guild_id}", encoding=None)
    await tr.execute()
    return {k: load_emojis(await v) for k, v in guild_data.items()}


def load_emojis(d):
    return [MessageToDict(EmojiData.FromString(v), preserving_proto_field_name=True, use_integers_for_enums=True, including_default_value_fields=True) for v in d.values()]
