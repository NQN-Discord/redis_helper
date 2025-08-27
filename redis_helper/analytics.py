from aioredis import Redis
from sentry_sdk import add_breadcrumb, start_span


def add_analytics(name: str, redis: Redis):
    async def execute(self, command, *args, **kwargs):
        add_breadcrumb(
            message=f"Requested from {name} Redis",
            category="redis",
            data={
                "command": command,
                "args": args
            }
        )

        with start_span(
            op="redis",
            name=f"{command.decode('utf-8')} {args}",
        ):
            return await self._pool_or_conn.execute(command, *args, **kwargs)
    redis.execute = execute.__get__(redis, type(redis))
