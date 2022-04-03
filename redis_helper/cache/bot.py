from aioredis import Redis
from datetime import datetime, timezone
from math import ceil
import msgpack
from ..protobuf.discord_pb2 import MeMemberData
from google.protobuf.json_format import MessageToDict


async def assign_me(redis: Redis, user):
    await redis.set("user", msgpack.packb(user))


async def fetch_me(redis: Redis):
    return msgpack.unpackb(await redis.get("user", encoding=None))


async def assign_member(redis: Redis, member):
    tr = redis.multi_exec()
    guild_id = member["guild_id"]
    _assign_member(tr, guild_id, member)
    await tr.execute()


def _assign_member(tr, guild_id, member):
    roles = member["roles"]
    nick = member.get("nick")
    communication_disabled_until = member.get("communication_disabled_until")
    if communication_disabled_until:
        # Convert to seconds past epoch, rounding up milliseconds.
        communication_disabled_until = int(ceil(datetime.fromisoformat(communication_disabled_until).timestamp()))
    tr.set(
        f"mem-{guild_id}",
        MeMemberData(
            roles=[int(r) for r in roles],
            nick=nick,
            communication_disabled_until=communication_disabled_until
        ).SerializeToString())


def get_member(member_bytes: bytes):
    member_data = MessageToDict(MeMemberData.FromString(member_bytes or b""), preserving_proto_field_name=True, use_integers_for_enums=True, including_default_value_fields=True)
    member_data["communication_disabled_until"] = datetime.fromtimestamp(
        int(member_data["communication_disabled_until"]),
        tz=timezone.utc
    ).isoformat()
    return member_data
