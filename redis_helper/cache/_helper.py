from typing import Awaitable, Tuple
import ujson as json

GUILD_ATTRS = ("name", "icon", "owner_id", "joined_at", "member_count", "system_channel_id", "premium_tier")


class OptionallyAwaitable:
    def __init__(self, *awaitables: Awaitable):
        self.awaitables = awaitables

    def __await__(self):
        for i in self.awaitables:
            yield from i.__await__()


def guild_keys(guild_id) -> Tuple:
    return f"guild-{guild_id}", f"roles-{guild_id}", f"role-perms-{guild_id}", f"channels-{guild_id}", f"emojis-{guild_id}", f"me-{guild_id}", f"nick-{guild_id}"


def parse_roles(tr, guild_id, roles):
    # The @everyone role is always present, so the roles list always has at least one element.
    return OptionallyAwaitable(
        tr.hmset_dict(f"roles-{guild_id}", {role["id"]: json.dumps(role) for role in roles}),
        tr.hmset_dict(f"role-perms-{guild_id}", {role["id"]: role["permissions"] for role in roles}),
    )


def parse_channels(tr, guild_id, channels):
    if not channels:
        return
    return tr.hmset_dict(f"channels-{guild_id}", {channel["id"]: json.dumps(channel) for channel in channels})


def parse_emojis(tr, guild_id, emojis):
    if not emojis:
        return
    return tr.hmset_dict(f"emojis-{guild_id}", {emoji["id"]: json.dumps(emoji) for emoji in emojis})
