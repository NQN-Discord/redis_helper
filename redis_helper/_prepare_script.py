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


_evaluated = set()


def prepare_script_for_transaction(script: str):
    script = script.encode()
    script_hash = sha1(script).hexdigest()

    def _call_function(redis, **kwargs):
        if script_hash in _evaluated:
            return redis.evalsha(script_hash, **kwargs)
        else:
            redis.eval(script, **kwargs)
            _evaluated.add(script_hash)
    return _call_function
