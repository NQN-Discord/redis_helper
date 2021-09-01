from aioredis import Redis
from sentry_sdk import add_breadcrumb


def add_analytics(name: str, redis: Redis):
    def execute(self, command, *args, **kwargs):
        add_breadcrumb(
            message=f"Requested from {name} Redis",
            category="redis",
            data={
                "command": command,
                "args": args
            }
        )

        return self._pool_or_conn.execute(command, *args, **kwargs)
    redis.execute = execute.__get__(redis, type(redis))
