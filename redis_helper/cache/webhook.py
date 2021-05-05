from typing import List, Tuple, Optional, Iterator, NoReturn
from aioredis import Redis


async def assign_channel(redis: Redis, channel_id: int, webhooks: Iterator[Tuple[int, int, str]]) -> NoReturn:
    key = f"webhooks-channel-cache-{channel_id}"
    if not webhooks:
        await redis.delete(key)
    else:
        tr = redis.multi_exec()
        tr.delete(key)
        tr.rpush(key, *[f"{id}-{user_id}-{token}" for id, user_id, token in webhooks])
        tr.expire(key, 15 * 60)
        await tr.execute()


async def fetch_channel(redis: Redis, channel_id: int) -> List[Tuple[int, str]]:
    key = f"webhooks-channel-cache-{channel_id}"
    webhooks = await redis.lrange(key, 0, -1)
    return [(int(id), int(user_id), token) for id, user_id, token in (webhook.split("-", 2) for webhook in webhooks)]


async def assign_latest_user(
        redis: Redis,
        channel_id: int,
        user_id: Optional[int],
        owner_id: Optional[int],
        webhook_id: Optional[int],
        webhook_token: Optional[str]
) -> NoReturn:
    key = f"webhook-last-user-cache-{channel_id}"
    if webhook_id is None or webhook_token is None or user_id is None:
        await redis.delete(key)
    else:
        await redis.set(key, f"{user_id}-{webhook_id}-{owner_id}-{webhook_token}", expire=15 * 60)


async def fetch_latest_user(redis: Redis, channel_id: int) -> Optional[Tuple[int, int, int, str]]:
    webhook = await redis.get(f"webhook-last-user-cache-{channel_id}")
    if webhook is not None:
        user_id, webhook_id, owner_id, token = webhook.split("-", 3)
        return int(user_id), int(webhook_id), int(owner_id), token
