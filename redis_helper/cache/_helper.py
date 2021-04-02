from typing import Awaitable, Tuple
from ..protobuf.discord_pb2 import RoleData, ChannelData, EmojiData

GUILD_ATTRS = ("name", "icon", "owner_id", "joined_at", "member_count", "system_channel_id", "premium_tier")


class OptionallyAwaitable:
    def __init__(self, *awaitables: Awaitable):
        self.awaitables = awaitables

    def __await__(self):
        for i in self.awaitables:
            yield from i.__await__()


def guild_keys(guild_id) -> Tuple:
    return f"guild-{guild_id}", f"roles-{guild_id}", f"channels-{guild_id}", f"emojis-{guild_id}", f"me-{guild_id}", f"nick-{guild_id}"


def parse_roles(tr, guild_id, roles):
    # The @everyone role is always present, so the roles list always has at least one element.
    return OptionallyAwaitable(
        tr.hmset_dict(f"roles-{guild_id}", {role["id"]: RoleData(
            id=int(role["id"]),
            name=role["name"],
            position=role["position"],
            permissions=int(role["permissions"]),
            mentionable=role["mentionable"],
            managed=role["managed"],
            bot_id="tags" in role and "bot_id" in role["tags"] and int(role["tags"]["bot_id"])
        ).SerializeToString() for role in roles})
    )


def parse_channels(tr, guild_id, channels):
    for channel in range(len(channels)-1, -1, -1):
        if channels[channel]["type"] not in (0, 5):
            del channels[channel]

    if not channels:
        return
    return tr.hmset_dict(f"channels-{guild_id}", {channel["id"]:  ChannelData(
            id=int(channel["id"]),
            name=channel["name"],
            type=channel["type"],
            rate_limit_per_user=channel.get("rate_limit_per_user"),
            position=channel["position"],
            permission_overwrites=(
                ChannelData.ChannelPermissionOverwriteData(
                    type=overwrite["type"],
                    id=int(overwrite["id"]),
                    deny=int(overwrite["deny"]),
                    allow=int(overwrite["allow"]),
                )
                for overwrite in channel["permission_overwrites"]
            ),
        ).SerializeToString() for channel in channels})


def parse_emojis(tr, guild_id, emojis):
    if not emojis:
        return
    return tr.hmset_dict(f"emojis-{guild_id}", {emoji["id"]: EmojiData(
            id=int(emoji["id"]),
            name=emoji["name"],
            available=emoji["available"],
            animated=emoji["animated"],
            roles=(int(i) for i in emoji["roles"]),
        ).SerializeToString() for emoji in emojis})
