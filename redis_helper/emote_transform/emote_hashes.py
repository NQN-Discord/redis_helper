from typing import List, Optional, NoReturn, Iterable
from aioredis import Redis

hitters_script = """
local set = ARGV[1]
local key = ARGV[3]
local set_length = tonumber(ARGV[2])

if redis.call('ZRANK', set, key) then
    redis.call('ZINCRBY', set, 1.0, key)
elseif redis.call('ZCARD', set) < set_length then
    redis.call('ZADD', set, 1.0, key)
else
    local value = redis.call('ZRANGE', set,0,0, 'withscores')
    redis.call('ZREM', set, value[1])
    redis.call('ZADD', set, value[2] + 1.0, key)
end
"""
