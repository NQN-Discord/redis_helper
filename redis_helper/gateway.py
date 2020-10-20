from typing import Dict, Optional
from math import isfinite


async def fetch_latency(redis) -> Dict[int, Optional[float]]:
    tr = redis.pipeline()
    no_shards = int(await redis.get("gateway-shard-count"))
    latency_futures = {shard_id: tr.get(f"gateway-shard-latency-{shard_id}") for shard_id in range(no_shards)}
    await tr.execute()
    latencies = {}
    for k, v in latency_futures.items():
        latency = await v
        latencies[k] = latency = latency and float(latency)
        if latency is not None and not isfinite(latency):
            latencies[k] = None
    return latencies
