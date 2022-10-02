from itertools import chain

from aioredis import Redis, MultiExecError
from aioredis.commands import MultiExec

from redis_helper._prepare_script import prepare_script_for_transaction, _evaluated

assign_hashmap_keep_ttl_script = prepare_script_for_transaction("""
local guild_id = ARGV[1]
ARGV[1] = KEYS[1]

local last_read_time = redis.call('ZSCORE', KEYS[2], guild_id)
if last_read_time then
    redis.call('HMSET', unpack(ARGV))
    redis.call('PEXPIREAT', KEYS[1], math.floor(last_read_time / 1000000) + 172800000)
end
""")


def assign_hashmap_keep_ttl(redis: Redis, guild_id: int):
    def _inner(key, dict_to_set):
        redis.delete(key)
        if dict_to_set:
            assign_hashmap_keep_ttl_script(
                redis,
                keys=[key, "guild_last_read"],
                args=[
                    guild_id,
                    *chain.from_iterable(dict_to_set.items())
                ]
            )
    return _inner


async def execute_transaction(tr: MultiExec, on_fail):
    try:
        await tr.execute()
    except MultiExecError as e:
        if e.args[1][0].args == ('NOSCRIPT No matching script. Please use EVAL.',):
            _evaluated.clear()
            await on_fail()
        else:
            raise
