from typing import Dict, Optional, Any, List
from math import isfinite
import json


async def fetch_latency(redis) -> Dict[int, Optional[float]]:
    tr = redis.pipeline()
    no_shards = int(await redis.get("gateway-shard-count"))
    latency_futures = {shard_id: tr.get(f"gateway-shard-latency-{shard_id}") for shard_id in range(no_shards)}
    await tr.execute()
    latencies = {}
    for k, v in latency_futures.items():
        latency = await v
        latencies[k] = latency = latency and float(latency)
        if latency in (None, "") or not isfinite(latency):
            latencies[k] = None
    return latencies


async def assign_latencies(redis, shard_count: int, latencies: Dict[int, float], timeout: int):
    tr = redis.pipeline()
    tr.set("gateway-shard-count", shard_count)
    for shard_id, latency in latencies.items():
        tr.set(f"gateway-shard-latency-{shard_id}", latency, expire=timeout)
    await tr.execute()


async def assign_resumable_shards(
        redis,
        connection_id: str,
        shards: Dict[int, Dict[str, Any]],
        total_shards: int,
        timeout: float
):
    tr = redis.pipeline()
    tr.set(f"gateway-resume-{connection_id}", total_shards, expire=timeout)
    for shard_id, session_info in shards.items():
        tr.set(f"gateway-shard-resume-{shard_id}", json.dumps(session_info), expire=timeout)
    await tr.execute()


async def fetch_shard_count(redis, connection_id: str):
    count = await redis.get(f"gateway-resume-{connection_id}")
    if count is not None:
        return int(count)


async def fetch_session_info(redis, shard_id: int):
    session_info = await redis.get(f"gateway-shard-resume-{shard_id}")
    if session_info is not None:
        return json.loads(session_info)
