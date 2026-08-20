"""
benchmark_cypher.py

Benchmark query runner for any Bolt/Cypher-compatible graph database:
CognoDB, Memgraph, and local Neo4j all use this same runner,
just with different connection credentials.

Measures, per the assignment's required metrics:
    - 1-hop, 2-hop, 3-hop traversal latency (p50, p95)
    - Point lookup latency (p50, p95)
    - Indexed/filtered lookup latency (p50, p95)
    - Aggregation (count/group-by) latency (p50, p95)
    - Concurrent read/write throughput (queries/sec at N concurrent clients)

Usage:
    python3 benchmark_cypher.py

Requires:
    pip install neo4j python-dotenv

Expects the database to already be loaded (run the matching loader_*.py first).
"""

import os
import time
import json
import random
import statistics
import concurrent.futures
from neo4j import GraphDatabase

ITERATIONS = 100          # per read workload, after warm-up
WARMUP_ITERATIONS = 10
CONCURRENT_CLIENTS = 10
CONCURRENT_DURATION_SEC = 30


def percentile(values, pct):
    """Simple percentile calc without extra dependencies."""
    if not values:
        return None
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * pct / 100)
    idx = min(idx, len(sorted_vals) - 1)
    return sorted_vals[idx]


def timed_run(session, query, params=None):
    start = time.perf_counter()
    session.run(query, params or {}).consume()
    return (time.perf_counter() - start) * 1000  # ms


def get_sample_node_ids(driver, sample_size=200):
    """Pull a random-ish sample of node IDs to use as traversal/lookup start points."""
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Person) RETURN p.id AS id ORDER BY rand() LIMIT $n",
            n=sample_size,
        )
        return [record["id"] for record in result]


def benchmark_traversals(driver, sample_ids, platform_name):
    results = {}
    hop_queries = {
        "1_hop": """
            MATCH (p:Person {id: $id})-[:FRIENDS_WITH]->(f)
            RETURN count(f) AS c
        """,
        "2_hop": """
            MATCH (p:Person {id: $id})-[:FRIENDS_WITH*2]->(f)
            RETURN count(DISTINCT f) AS c
        """,
        "3_hop": """
            MATCH (p:Person {id: $id})-[:FRIENDS_WITH*3]->(f)
            RETURN count(DISTINCT f) AS c
        """,
    }

    for label, query in hop_queries.items():
        # warm-up
        with driver.session() as session:
            for i in range(WARMUP_ITERATIONS):
                node_id = random.choice(sample_ids)
                timed_run(session, query, {"id": node_id})

        # measured
        latencies = []
        with driver.session() as session:
            for i in range(ITERATIONS):
                node_id = random.choice(sample_ids)
                latencies.append(timed_run(session, query, {"id": node_id}))

        results[label] = {
            "p50_ms": round(percentile(latencies, 50), 2),
            "p95_ms": round(percentile(latencies, 95), 2),
            "iterations": ITERATIONS,
        }
        print(f"[{platform_name}] {label}: p50={results[label]['p50_ms']}ms "
              f"p95={results[label]['p95_ms']}ms")

    return results


def benchmark_point_lookup(driver, sample_ids, platform_name):
    query = "MATCH (p:Person {id: $id}) RETURN p.id AS id"

    with driver.session() as session:
        for i in range(WARMUP_ITERATIONS):
            timed_run(session, query, {"id": random.choice(sample_ids)})

    latencies = []
    with driver.session() as session:
        for i in range(ITERATIONS):
            latencies.append(timed_run(session, query, {"id": random.choice(sample_ids)}))

    result = {
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "iterations": ITERATIONS,
        "indexed": True,  # Person.id has an index from the loader step
    }
    print(f"[{platform_name}] point_lookup: p50={result['p50_ms']}ms p95={result['p95_ms']}ms")
    return result


def benchmark_aggregation(driver, platform_name):
    # Count relationships per node, grouped -- a realistic group-by style query
    query = """
        MATCH (p:Person)-[:FRIENDS_WITH]->(f)
        RETURN p.id AS id, count(f) AS degree
        ORDER BY degree DESC
        LIMIT 100
    """

    with driver.session() as session:
        for i in range(WARMUP_ITERATIONS):
            timed_run(session, query)

    latencies = []
    with driver.session() as session:
        for i in range(ITERATIONS):
            latencies.append(timed_run(session, query))

    result = {
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "iterations": ITERATIONS,
        "query_description": "Top-100 nodes by out-degree (group-by style aggregation)",
    }
    print(f"[{platform_name}] aggregation: p50={result['p50_ms']}ms p95={result['p95_ms']}ms")
    return result


def _mixed_workload_worker(uri, user, password, sample_ids, stop_time, counters, lock):
    """Runs in its own thread/connection -- mixes reads and writes until stop_time."""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    local_count = 0
    try:
        with driver.session() as session:
            while time.time() < stop_time:
                if random.random() < 0.8:
                    # 80% reads: point lookup
                    node_id = random.choice(sample_ids)
                    session.run(
                        "MATCH (p:Person {id: $id}) RETURN p.id",
                        id=node_id,
                    ).consume()
                else:
                    # 20% writes: update a property (non-destructive, repeatable)
                    node_id = random.choice(sample_ids)
                    session.run(
                        "MATCH (p:Person {id: $id}) SET p.touched = timestamp() RETURN p.id",
                        id=node_id,
                    ).consume()
                local_count += 1
    finally:
        driver.close()
        with lock:
            counters.append(local_count)


def benchmark_mixed_workload(uri, user, password, sample_ids, platform_name,
                              clients=CONCURRENT_CLIENTS, duration=CONCURRENT_DURATION_SEC):
    import threading
    counters = []
    lock = threading.Lock()
    stop_time = time.time() + duration

    print(f"[{platform_name}] Running mixed read/write workload: "
          f"{clients} concurrent clients for {duration}s (80% read / 20% write)...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=clients) as executor:
        futures = [
            executor.submit(_mixed_workload_worker, uri, user, password,
                             sample_ids, stop_time, counters, lock)
            for _ in range(clients)
        ]
        concurrent.futures.wait(futures)

    total_ops = sum(counters)
    throughput = total_ops / duration

    result = {
        "concurrent_clients": clients,
        "duration_sec": duration,
        "read_write_mix": "80/20",
        "total_operations": total_ops,
        "queries_per_sec": round(throughput, 1),
    }
    print(f"[{platform_name}] mixed_workload: {result['queries_per_sec']} queries/sec "
          f"({total_ops} total ops)")
    return result


def run_benchmark(uri, user, password, platform_name):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    print(f"\n=== Benchmarking {platform_name} ===")
    sample_ids = get_sample_node_ids(driver, sample_size=200)
    print(f"[{platform_name}] Sampled {len(sample_ids)} node IDs for read workloads.")

    results = {
        "platform": platform_name,
        "traversals": benchmark_traversals(driver, sample_ids, platform_name),
        "point_lookup": benchmark_point_lookup(driver, sample_ids, platform_name),
        "aggregation": benchmark_aggregation(driver, platform_name),
    }

    driver.close()

    # Mixed workload opens its own connections per thread, so run it after closing the main driver
    results["mixed_workload"] = benchmark_mixed_workload(
        uri, user, password, sample_ids, platform_name
    )

    return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    all_results = []

    # --- CognoDB ---
    all_results.append(run_benchmark(
        uri=os.environ["COGNODB_URI"],
        user=os.environ["COGNODB_USER"],
        password=os.environ["COGNODB_PASSWORD"],
        platform_name="CognoDB",
    ))

    # --- Memgraph (using neo4j driver directly here for Cypher benchmarking;
    #     note your loader used gqlalchemy, but Memgraph also speaks raw Bolt,
    #     so the neo4j driver works fine for querying too) ---
    all_results.append(run_benchmark(
        uri=os.environ["MEMGRAPH_URI"] if "MEMGRAPH_URI" in os.environ
            else f"bolt+s://{os.environ['MEMGRAPH_HOST']}:{os.environ['MEMGRAPH_PORT']}",
        user=os.environ.get("MEMGRAPH_USERNAME", os.environ.get("MEMGRAPH_USER")),
        password=os.environ.get("MEMGRAPH_PASSWORD"),
        platform_name="Memgraph",
    ))

    # --- Local Neo4j ---
    all_results.append(run_benchmark(
        uri=os.environ["LOCAL_NEO4J_URI"],
        user=os.environ["LOCAL_NEO4J_USER"],
        password=os.environ["LOCAL_NEO4J_PASSWORD"],
        platform_name="Neo4j-Local",
    ))

    print("\n--- Benchmark Summary ---")
    for r in all_results:
        print(json.dumps(r, indent=2))

    os.makedirs("results", exist_ok=True)
    with open("results/benchmark_results_cypher.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved results/benchmark_results_cypher.json")
