"""Simple async load test utility for ContentIQ metadata APIs."""

import argparse
import asyncio
import time

import httpx


async def push(client: httpx.AsyncClient, index: int) -> None:
    payload = {
        "key": f"asset-{index}",
        "value": {"owner": "content-team", "region": "us", "sequence": index},
        "tags": ["load-test", "metadata"],
    }
    response = await client.post("/api/v1/metadata", json=payload)
    response.raise_for_status()


async def run(base_url: str, total_requests: int, concurrency: int) -> None:
    start = time.perf_counter()
    limits = httpx.Limits(max_connections=concurrency)

    async with httpx.AsyncClient(base_url=base_url, timeout=15.0, limits=limits) as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded(index: int) -> None:
            async with semaphore:
                await push(client, index)

        await asyncio.gather(*(bounded(i) for i in range(total_requests)))

    elapsed = time.perf_counter() - start
    rps = total_requests / elapsed
    projected_daily = rps * 86400

    print(f"Total requests: {total_requests}")
    print(f"Elapsed seconds: {elapsed:.2f}")
    print(f"Requests/sec: {rps:.2f}")
    print(f"Projected requests/day: {projected_daily:,.0f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--total-requests", type=int, default=10000)
    parser.add_argument("--concurrency", type=int, default=200)
    args = parser.parse_args()

    asyncio.run(run(args.base_url, args.total_requests, args.concurrency))
