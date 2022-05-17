from hashlib import sha1
from aioredis import ReplyError


def prepare_script(script: str):
    script = script.encode()
    script_hash = sha1(script).hexdigest()

    async def _call_function(redis, **kwargs):
        try:
            await redis.evalsha(script_hash, **kwargs)
        except ReplyError:
            await redis.eval(script, **kwargs)
    return _call_function