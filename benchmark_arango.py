"""
benchmark_arango.py

Benchmark query runner for ArangoDB Oasis.

Measures the same required metrics as benchmark_cypher.py, translated to AQL:
    - 1-hop, 2-hop, 3-hop traversal latency (p50, p95)
    - Point lookup latency (p50, p95)
    - Indexed/filtered lookup latency (p50, p95)
    - Aggregation (count/group-by) latency (p50, p95)
    - Concurrent read/write throughput (queries/sec at N concurrent clients)

Usage:
    python3 benchmark_arango.py

Requires:
    pip install python-arango python-dotenv

Expects the database to already be loaded (run loader_arango.py first),
and expects the same cert_file.crt written by that loader to still be
present (or re-decodes it fresh from ARANGO_CA_B64 if missing).
"""

import os
import csv
import time
import json
import base64
import random
import threading
import concurrent.futures
from arango import ArangoClient

ITERATIONS = 100
WARMUP_ITERATIONS = 10
CONCURRENT_CLIENTS = 10
CONCURRENT_DURATION_SEC = 30
CERT_PATH = "cert_file.crt"


def percentile(values, pct):
    if not values:
        return None
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * pct / 100)
    idx = min(idx, len(sorted_vals) - 1)
    return sorted_vals[idx]


def ensure_ca_cert():
    """Writes the CA cert to disk if it isn't already there (loader_arango.py
    normally does this, but the benchmark script can run independently too)."""
    if os.path.exists(CERT_PATH):
        return
    encoded_ca = os.environ["ARANGO_CA_B64"]
    file_content = base64.b64decode(encoded_ca)
    with open(CERT_PATH, "w+") as f:
        f.write(file_content.decode("utf-8"))
    print("[ArangoDB] CA cert written.")


def connect():
    host = os.environ["ARANGO_HOST"]
    user = os.environ["ARANGO_USER"]
    password = os.environ["ARANGO_PASSWORD"]
    db_name = os.environ["ARANGO_DB"]

    client = ArangoClient(hosts=host, verify_override=CERT_PATH)
    db = client.db(db_name, username=user, password=password)
    return db


def timed_run(db, query, bind_vars=None):
    start = time.perf_counter()
    cursor = db.aql.execute(query, bind_vars=bind_vars or {})
    list(cursor)  # fully consume, same as .consume() on the Cypher side
    return (time.perf_counter() - start) * 1000  # ms


def get_sample_node_ids(db, sample_size=200):
    query = """
        FOR doc IN nodes
        SORT RAND()
        LIMIT @n
        RETURN doc.person_id
    """
    cursor = db.aql.execute(query, bind_vars={"n": sample_size})
    return list(cursor)


def benchmark_traversals(db, sample_ids, platform_name):
    results = {}
    hop_queries = {
        "1_hop": """
            FOR v IN 1..1 OUTBOUND @start_vertex edges
            COLLECT WITH COUNT INTO c
            RETURN c
        """,
        "2_hop": """
            FOR v IN 2..2 OUTBOUND @start_vertex edges
            COLLECT WITH COUNT INTO c
            RETURN c
        """,
        "3_hop": """
            FOR v IN 3..3 OUTBOUND @start_vertex edges
            COLLECT WITH COUNT INTO c
            RETURN c
        """,
    }

    for label, query in hop_queries.items():
        for i in range(WARMUP_ITERATIONS):
            node_id = random.choice(sample_ids)
            timed_run(db, query, {"start_vertex": f"nodes/{node_id}"})

        latencies = []
        for i in range(ITERATIONS):
            node_id = random.choice(sample_ids)
            latencies.append(timed_run(db, query, {"start_vertex": f"nodes/{node_id}"}))

        results[label] = {
            "p50_ms": round(percentile(latencies, 50), 2),
            "p95_ms": round(percentile(latencies, 95), 2),
            "iterations": ITERATIONS,
        }
        print(f"[{platform_name}] {label}: p50={results[label]['p50_ms']}ms "
              f"p95={results[label]['p95_ms']}ms")

    return results


def benchmark_point_lookup(db, sample_ids, platform_name):
    """Direct document lookup by _key -- the ArangoDB-native equivalent of a
    primary-key point lookup, generally the fastest possible read."""
    nodes = db.collection("nodes")

    for i in range(WARMUP_ITERATIONS):
        nodes.get(str(random.choice(sample_ids)))

    latencies = []
    for i in range(ITERATIONS):
        node_id = str(random.choice(sample_ids))
        start = time.perf_counter()
        nodes.get(node_id)
        latencies.append((time.perf_counter() - start) * 1000)

    result = {
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "iterations": ITERATIONS,
        "method": "direct _key document lookup",
    }
    print(f"[{platform_name}] point_lookup: p50={result['p50_ms']}ms p95={result['p95_ms']}ms")
    return result


def benchmark_indexed_lookup(db, sample_ids, platform_name):
    """AQL filter on the indexed person_id field -- distinct from the direct
    _key lookup above, since this exercises the persistent index created
    by loader_arango.py rather than the primary key path."""
    query = """
        FOR doc IN nodes
        FILTER doc.person_id == @id
        RETURN doc
    """

    for i in range(WARMUP_ITERATIONS):
        timed_run(db, query, {"id": random.choice(sample_ids)})

    latencies = []
    for i in range(ITERATIONS):
        latencies.append(timed_run(db, query, {"id": random.choice(sample_ids)}))

    result = {
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "iterations": ITERATIONS,
        "indexed": True,
        "indexed_field": "person_id (persistent index)",
    }
    print(f"[{platform_name}] indexed_lookup: p50={result['p50_ms']}ms p95={result['p95_ms']}ms")
    return result


def benchmark_aggregation(db, platform_name):
    query = """
        FOR v, e IN 1..1 OUTBOUND nodes edges
        COLLECT node = v._id WITH COUNT INTO degree
        SORT degree DESC
        LIMIT 100
        RETURN {id: node, degree: degree}
    """
    # Note: ArangoDB AQL traversal requires a concrete start vertex or
    # collection expression -- this variant aggregates degree across all
    # nodes via the edges collection directly instead, which is the more
    # idiomatic AQL way to do a graph-wide group-by:
    query = """
        FOR e IN edges
        COLLECT node = e._from WITH COUNT INTO degree
        SORT degree DESC
        LIMIT 100
        RETURN {id: node, degree: degree}
    """

    for i in range(WARMUP_ITERATIONS):
        timed_run(db, query)

    latencies = []
    for i in range(ITERATIONS):
        latencies.append(timed_run(db, query))

    result = {
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "iterations": ITERATIONS,
        "query_description": "Top-100 nodes by out-degree (group-by style aggregation)",
    }
    print(f"[{platform_name}] aggregation: p50={result['p50_ms']}ms p95={result['p95_ms']}ms")
    return result


def _mixed_workload_worker(sample_ids, stop_time, counters, lock):
    """Each thread opens its own ArangoDB connection -- python-arango's
    client/db objects are not guaranteed thread-safe, so sharing one across
    threads would risk corrupting results rather than reflecting real
    concurrent-client behaviour."""
    db = connect()
    nodes = db.collection("nodes")
    local_count = 0
    while time.time() < stop_time:
        if random.random() < 0.8:
            # 80% reads: point lookup
            node_id = str(random.choice(sample_ids))
            nodes.get(node_id)
        else:
            # 20% writes: update a property (non-destructive, repeatable)
            node_id = str(random.choice(sample_ids))
            nodes.update({"_key": node_id, "touched": time.time()})
        local_count += 1
    with lock:
        counters.append(local_count)


def benchmark_mixed_workload(sample_ids, platform_name,
                              clients=CONCURRENT_CLIENTS, duration=CONCURRENT_DURATION_SEC):
    counters = []
    lock = threading.Lock()
    stop_time = time.time() + duration

    print(f"[{platform_name}] Running mixed read/write workload: "
          f"{clients} concurrent clients for {duration}s (80% read / 20% write)...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=clients) as executor:
        futures = [
            executor.submit(_mixed_workload_worker, sample_ids, stop_time, counters, lock)
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


def run_benchmark(platform_name="ArangoDB"):
    ensure_ca_cert()
    db = connect()

    print(f"\n=== Benchmarking {platform_name} ===")
    sample_ids = get_sample_node_ids(db, sample_size=200)
    print(f"[{platform_name}] Sampled {len(sample_ids)} node IDs for read workloads.")

    results = {
        "platform": platform_name,
        "traversals": benchmark_traversals(db, sample_ids, platform_name),
        "point_lookup": benchmark_point_lookup(db, sample_ids, platform_name),
        "indexed_lookup": benchmark_indexed_lookup(db, sample_ids, platform_name),
        "aggregation": benchmark_aggregation(db, platform_name),
        "mixed_workload": benchmark_mixed_workload(sample_ids, platform_name),
    }

    return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    try:
        result = run_benchmark()
        print("\n--- ArangoDB Benchmark Summary ---")
        print(json.dumps(result, indent=2))

        os.makedirs("results", exist_ok=True)
        with open("results/benchmark_results_arangodb.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\nSaved results/benchmark_results_arangodb.json")

    except Exception as e:
        print(f"\n!!! ArangoDB benchmark FAILED: {e}\n")
        raise
