from typing import List
from aioredis import Redis
from collections import defaultdict
import datetime
from .._prepare_script import prepare_script


EMOJI_COUNT_PER_DAY = 400
hitters_script = prepare_script(f"""
local set = KEYS[1]
local set_length = {EMOJI_COUNT_PER_DAY}

for i, key in ipairs(ARGV) do
    if redis.call('ZRANK', set, key) then
        redis.call('ZINCRBY', set, 1.0, key)
    elseif redis.call('ZCARD', set) < set_length then
        redis.call('ZADD', set, 1.0, key)
    else
        local value = redis.call('ZRANGE', set,0,0, 'withscores')
        redis.call('ZREM', set, value[1])
        redis.call('ZADD', set, value[2] + 1.0, key)
    end
end
""")


async def add_hashes(redis: Redis, hashes: List[str]):
    day_number = datetime.date.today().weekday()
    await hitters_script(redis, keys=[f"emoji-heavy-hitters-{day_number}"], args=hashes)


async def get_hashes(redis: Redis):
    pipeline = redis.pipeline()
    for day_number in range(7):
        pipeline.zrevrange(f"emoji-heavy-hitters-{day_number}", 0, EMOJI_COUNT_PER_DAY, withscores=True)
    results = await pipeline.execute()
    rtn = defaultdict(lambda: 0)
    for day in results:
        for emote_hash, score in day:
            rtn[emote_hash] += score
    return sorted(rtn, key=rtn.get, reverse=True)


async def delete_day(redis: Redis, date):
    day_number = date.weekday()
    await redis.delete(f"emoji-heavy-hitters-{day_number}")
