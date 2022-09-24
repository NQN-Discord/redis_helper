def _execute(redis, *args):
    return redis.__getattr__("execute")(*args)
