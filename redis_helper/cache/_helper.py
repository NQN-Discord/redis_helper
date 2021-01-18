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
    return f"guild-{guild_id}", f"roles-{guild_id}", f"channels-{guild_id}", f"emojis-{guild_id}", f"me-{guild_id}", f"nick-{guild_id}"


def parse_roles(tr, guild_id, roles):
    # The @everyone role is always present, so the roles list always has at least one element.
    for role in roles:
        role.pop("permissions_new", None)
        role.pop("color", None)
        role.pop("hoist", None)
    return OptionallyAwaitable(
        tr.hmset_dict(f"roles-{guild_id}", {role["id"]: json.dumps(role) for role in roles})
    )


def parse_channels(tr, guild_id, channels):
    for channel in range(len(channels)-1, -1, -1):
        if channels[channel]["type"] in (0, 1, 5):
            channels[channel].pop("topic", None)
            channels[channel].pop("last_message_id", None)
            channels[channel].pop("last_pin_timestamp", None)
            channels[channel].pop("parent_id", None)
            for perm_override in channels[channel].get("permission_overwrites", []):
                del perm_override["deny_new"]
                del perm_override["allow_new"]
        else:
            del channels[channel]

    if not channels:
        return
    return tr.hmset_dict(f"channels-{guild_id}", {channel["id"]: json.dumps(channel) for channel in channels})


def parse_emojis(tr, guild_id, emojis):
    if not emojis:
        return
    for emoji in emojis:
        emoji.pop("require_colons", None)
        emoji.pop("managed", None)
        emoji.pop("user", None)
    return tr.hmset_dict(f"emojis-{guild_id}", {emoji["id"]: json.dumps(emoji) for emoji in emojis})
