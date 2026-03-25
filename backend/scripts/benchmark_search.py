import argparse
import statistics
import time

import httpx


def run(base_url: str, query: str, top_k: int, runs: int) -> None:
    latencies = []

    with httpx.Client(timeout=30.0) as client:
        for _ in range(runs):
            start = time.perf_counter()
            resp = client.get(
                f"{base_url.rstrip('/')}/api/search/",
                params={"query": query, "top_k": top_k},
            )
            elapsed = (time.perf_counter() - start) * 1000
            latencies.append(elapsed)
            resp.raise_for_status()

    print(f"runs={runs}")
    print(f"mean_ms={statistics.mean(latencies):.2f}")
    print(f"p95_ms={statistics.quantiles(latencies, n=20)[18]:.2f}")
    print(f"min_ms={min(latencies):.2f}")
    print(f"max_ms={max(latencies):.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark ASE search endpoint.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--query", default="email automation")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()

    run(args.base_url, args.query, args.top_k, args.runs)
