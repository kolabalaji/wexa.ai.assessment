# Cypher Benchmark Results

The Cypher benchmark was executed against all three Cypher-compatible graph databases:

* **CognoDB**
* **Memgraph**
* **Neo4j Local**

## Benchmark Command

```bash
python3 benchmark_cypher.py
```

## Benchmark Configuration

| Parameter               | Configuration |
| ----------------------- | ------------: |
| Read workload sample    |  200 node IDs |
| Traversal iterations    |           100 |
| Point lookup iterations |           100 |
| Aggregation iterations  |           100 |
| Mixed workload clients  |            10 |
| Mixed workload duration |    30 seconds |
| Read / Write ratio      |     80% / 20% |
| Latency metrics         |     P50 / P95 |

---

## 1. Traversal Performance

### 1-Hop Traversal

| Platform        |         P50 |         P95 |
| --------------- | ----------: | ----------: |
| CognoDB         |   235.16 ms |   243.00 ms |
| Memgraph        |   177.40 ms |   234.15 ms |
| **Neo4j Local** | **5.62 ms** | **8.88 ms** |

### 2-Hop Traversal

| Platform        |         P50 |         P95 |
| --------------- | ----------: | ----------: |
| CognoDB         |   234.39 ms |   242.60 ms |
| Memgraph        |   172.45 ms |   175.50 ms |
| **Neo4j Local** | **4.52 ms** | **7.17 ms** |

### 3-Hop Traversal

| Platform        |         P50 |          P95 |
| --------------- | ----------: | -----------: |
| CognoDB         |   233.51 ms |    238.15 ms |
| Memgraph        |   175.68 ms |    181.59 ms |
| **Neo4j Local** | **6.04 ms** | **15.01 ms** |

---

## 2. Point Lookup Performance

The point lookup benchmark uses an indexed `Person.id` lookup.

| Platform        |         P50 |         P95 |
| --------------- | ----------: | ----------: |
| CognoDB         |   235.62 ms |   245.30 ms |
| Memgraph        |   180.41 ms |   184.29 ms |
| **Neo4j Local** | **4.04 ms** | **6.45 ms** |

**Index:** `Person.id` — enabled for all three platforms.

---

## 3. Aggregation Performance

The aggregation benchmark identifies the **top 100 nodes by out-degree** using a group-by style aggregation.

| Platform        |          P50 |          P95 |
| --------------- | -----------: | -----------: |
| CognoDB         |    404.81 ms |    463.94 ms |
| Memgraph        |    224.93 ms |    230.56 ms |
| **Neo4j Local** | **41.12 ms** | **67.68 ms** |

---

## 4. Mixed Read/Write Workload

The mixed workload was executed using:

* **10 concurrent clients**
* **30-second duration**
* **80% reads**
* **20% writes**

| Platform        | Total Operations | Queries/sec |
| --------------- | ---------------: | ----------: |
| CognoDB         |            1,139 |        38.0 |
| Memgraph        |            1,566 |        52.2 |
| **Neo4j Local** |       **31,160** | **1,038.7** |

Neo4j Local achieved the highest throughput in this workload.

---

## 5. Overall Benchmark Comparison

### Latency

| Workload     | CognoDB P50 | Memgraph P50 | Neo4j Local P50 |
| ------------ | ----------: | -----------: | --------------: |
| 1-Hop        |   235.16 ms |    177.40 ms |     **5.62 ms** |
| 2-Hop        |   234.39 ms |    172.45 ms |     **4.52 ms** |
| 3-Hop        |   233.51 ms |    175.68 ms |     **6.04 ms** |
| Point Lookup |   235.62 ms |    180.41 ms |     **4.04 ms** |
| Aggregation  |   404.81 ms |    224.93 ms |    **41.12 ms** |

### Throughput

| Platform        | Mixed Workload QPS |
| --------------- | -----------------: |
| CognoDB         |               38.0 |
| Memgraph        |               52.2 |
| **Neo4j Local** |        **1,038.7** |

---

## 6. Key Observations

### Neo4j Local

Neo4j Local demonstrated the strongest benchmark performance across the tested workloads:

* Lowest P50 latency for all read workloads.
* Lowest P95 latency for point lookup and 1/2-hop traversals.
* Fastest aggregation performance.
* Significantly higher mixed-workload throughput.

### Memgraph

Memgraph outperformed CognoDB across the measured read workloads:

* Lower traversal latency.
* Lower point lookup latency.
* Faster aggregation.
* Higher mixed-workload throughput.

### CognoDB

CognoDB successfully completed all benchmark workloads and returned consistent results:

* All traversal workloads completed successfully.
* Indexed point lookup completed successfully.
* Aggregation workload completed successfully.
* Mixed read/write workload completed successfully.

The benchmark results provide a baseline for further optimization and comparison.

> **Important:** These results represent this specific benchmark environment and configuration. Database version, hardware, network latency, deployment topology, indexes, query plans, concurrency settings, and workload characteristics can significantly affect performance.

---

## 7. Benchmark Result File

The complete machine-readable benchmark results were saved to:

```text
results/benchmark_results_cypher.json
```

## Status

**Cypher benchmark: ✅ Completed**

| Platform    |          Status         |
| ----------- | :---------------------: |
| CognoDB     |      ✅ Benchmarked      |
| Memgraph    |      ✅ Benchmarked      |
| Neo4j Local |      ✅ Benchmarked      |
| ArangoDB    | ⏳ AQL benchmark pending |

The next step is to run the **ArangoDB AQL benchmark** and then consolidate all four platforms into the final performance comparison.

