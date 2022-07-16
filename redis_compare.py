import asyncio
import aioredis
from itertools import combinations

from redis_helper.cache.guild import fetch_guild_ids, fetch_guilds
import dictdiffer


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


async def get_all_keys(redis):
    all_keys = {}

    i = 0
    cur = b'0'
    while cur:
        cur, keys = await redis.scan(cur, count=10_000)
        i += 1
        print(i)
        tr = redis.multi_exec()
        dumps = [tr.dump(key) for key in keys]
        await tr.execute()
        dumps = await asyncio.gather(*dumps)
        for k, v in zip(keys, dumps):
            all_keys[k] = v
    return all_keys


async def read_guilds(redis):
    guild_ids = await fetch_guild_ids(redis)
    guilds = {}
    for i, chunk in enumerate(divide_chunks(guild_ids, 1000)):
        print(f"Chunk {i}")
        async for guild in fetch_guilds(redis, chunk, user=None, emojis=True):
            guilds[guild["id"]] = guild
            guild["channels"].sort(key=lambda c: c["id"])
            guild["roles"].sort(key=lambda c: c["id"])
            guild["emojis"].sort(key=lambda c: c["id"])
    return guilds


async def main():
    redis = await aioredis.create_redis_pool("redis://localhost", encoding=None)

    dbs_names = [0, 1]
    set_keys = set()
    dbs = {}
    for db_name in dbs_names:
        print(f"Loading {db_name}")
        await redis.select(db_name)
        dbs[db_name] = db = await read_guilds(redis)
        set_keys |= set(db.keys())

    print("Comparing...")
    for db1, db2 in combinations(dbs_names, 2):
        for guild_id in (i for i in set_keys if dbs[db1].get(i) != dbs[db2].get(i)):
            diff = list(dictdiffer.diff(dbs[db1].get(guild_id), dbs[db2].get(guild_id)))
            print(diff)

        print(db1, db2, sum(dbs[db1].get(i) != dbs[db2].get(i) for i in set_keys))
    print("Done!")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
