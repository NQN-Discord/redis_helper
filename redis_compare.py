import asyncio
import aioredis
from itertools import combinations


async def get_all_keys(redis):
    all_keys = {}

    i = 0
    cur = b'0'
    while cur:
        cur, keys = await redis.scan(cur, count=10_000)
        i += 1
        if i % 10 == 0:
            print(i)
        tr = redis.multi_exec()
        dumps = [tr.dump(key) for key in keys]
        await tr.execute()
        dumps = await asyncio.gather(*dumps)
        for k, v in zip(keys, dumps):
            all_keys[k] = v
    return all_keys


async def main():
    redis = await aioredis.create_redis_pool("redis://localhost", encoding=None)

    dbs_names = [1, 2, 3, 4, 5, 6, 7]
    set_keys = set()
    dbs = {}
    for db_name in dbs_names:
        print(f"Loading {db_name}")
        await redis.select(db_name)
        dbs[db_name] = db = await get_all_keys(redis)
        set_keys |= set(db.keys())

    print("Comparing...")
    for db1, db2 in combinations(dbs_names, 2):
        print(db1, db2, sum(dbs[db1].get(i) != dbs[db2].get(i) for i in set_keys))
    print("Done!")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
