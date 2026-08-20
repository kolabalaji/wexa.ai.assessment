# ArangoDB AQL Benchmark Results

The ArangoDB benchmark was successfully executed using **AQL** against the loaded SNAP soc-Pokec dataset.

## Benchmark Command

```bash
python3 benchmark_arango.py
```

## Benchmark Configuration

| Parameter                 | Configuration |
| ------------------------- | ------------: |
| Read workload sample      |  200 node IDs |
| Traversal iterations      |           100 |
| Point lookup iterations   |           100 |
| Indexed lookup iterations |           100 |
| Aggregation iterations    |           100 |
| Mixed workload clients    |            10 |
| Mixed workload duration   |    30 seconds |
| Read / Write ratio        |     80% / 20% |
| Latency metrics           |     P50 / P95 |

---

## 1. Traversal Performance

### 1-Hop Traversal

| Metric     |        Result |
| ---------- | ------------: |
| P50        | **268.59 ms** |
| P95        | **324.48 ms** |
| Iterations |           100 |

### 2-Hop Traversal

| Metric     |        Result |
| ---------- | ------------: |
| P50        | **263.78 ms** |
| P95        | **325.43 ms** |
| Iterations |           100 |

### 3-Hop Traversal

| Metric     |        Result |
| ---------- | ------------: |
| P50        | **261.21 ms** |
| P95        | **313.13 ms** |
| Iterations |           100 |

### Traversal Summary

| Workload |       P50 |       P95 |
| -------- | --------: | --------: |
| 1-Hop    | 268.59 ms | 324.48 ms |
| 2-Hop    | 263.78 ms | 325.43 ms |
| 3-Hop    | 261.21 ms | 313.13 ms |

---

## 2. Point Lookup Performance

ArangoDB was tested using a direct `_key` document lookup.

| Metric     |                        Result |
| ---------- | ----------------------------: |
| Method     | Direct `_key` document lookup |
| P50        |                 **261.64 ms** |
| P95        |                 **294.18 ms** |
| Iterations |                           100 |

---

## 3. Indexed Lookup Performance

An indexed lookup was also tested using the persistent index on:

```text
person_id
```

| Metric        |        Result |
| ------------- | ------------: |
| Indexed       |         ✅ Yes |
| Indexed Field |   `person_id` |
| Index Type    |    Persistent |
| P50           | **262.40 ms** |
| P95           | **304.93 ms** |
| Iterations    |           100 |

> **Note:** The indexed lookup and direct `_key` lookup produced similar latency in this benchmark. This result is specific to the current dataset, query implementation, and deployment environment.

---

## 4. Aggregation Performance

The aggregation benchmark identifies the **top 100 nodes by out-degree** using a group-by style aggregation.

| Metric     |        Result |
| ---------- | ------------: |
| P50        | **368.27 ms** |
| P95        | **611.15 ms** |
| Iterations |           100 |

The relatively higher P95 indicates greater latency variation under this aggregation workload.

---

## 5. Mixed Read/Write Workload

The mixed workload was executed with:

* **10 concurrent clients**
* **30-second duration**
* **80% reads**
* **20% writes**

| Metric             |               Result |
| ------------------ | -------------------: |
| Concurrent Clients |                   10 |
| Duration           |               30 sec |
| Read / Write Mix   |              80 / 20 |
| Total Operations   |            **1,077** |
| Throughput         | **35.9 queries/sec** |

---

## 6. ArangoDB Benchmark Summary

| Workload        |       P50 |       P95 |
| --------------- | --------: | --------: |
| 1-Hop Traversal | 268.59 ms | 324.48 ms |
| 2-Hop Traversal | 263.78 ms | 325.43 ms |
| 3-Hop Traversal | 261.21 ms | 313.13 ms |
| Point Lookup    | 261.64 ms | 294.18 ms |
| Indexed Lookup  | 262.40 ms | 304.93 ms |
| Aggregation     | 368.27 ms | 611.15 ms |
| Mixed Workload  |  35.9 QPS |         — |

---

## 7. Cross-Platform Benchmark Comparison

With the ArangoDB benchmark complete, all four platforms have now been benchmarked.

### Read Latency — P50

| Workload     |   CognoDB |  Memgraph |  Neo4j Local |  ArangoDB |
| ------------ | --------: | --------: | -----------: | --------: |
| 1-Hop        | 235.16 ms | 177.40 ms |  **5.62 ms** | 268.59 ms |
| 2-Hop        | 234.39 ms | 172.45 ms |  **4.52 ms** | 263.78 ms |
| 3-Hop        | 233.51 ms | 175.68 ms |  **6.04 ms** | 261.21 ms |
| Point Lookup | 235.62 ms | 180.41 ms |  **4.04 ms** | 261.64 ms |
| Aggregation  | 404.81 ms | 224.93 ms | **41.12 ms** | 368.27 ms |

### Mixed Workload Throughput

| Platform        | Queries/sec | Total Operations |
| --------------- | ----------: | ---------------: |
| CognoDB         |        38.0 |            1,139 |
| Memgraph        |        52.2 |            1,566 |
| **Neo4j Local** | **1,038.7** |       **31,160** |
| ArangoDB        |        35.9 |            1,077 |

Based on this benchmark run, **Neo4j Local achieved the highest throughput and lowest query latency** among the four tested platforms.

---

## 8. Results File

The complete machine-readable ArangoDB benchmark results were saved to:

```text
results/benchmark_results_arangodb.json
```

### Result JSON

```json
{
  "platform": "ArangoDB",
  "traversals": {
    "1_hop": {
      "p50_ms": 268.59,
      "p95_ms": 324.48,
      "iterations": 100
    },
    "2_hop": {
      "p50_ms": 263.78,
      "p95_ms": 325.43,
      "iterations": 100
    },
    "3_hop": {
      "p50_ms": 261.21,
      "p95_ms": 313.13,
      "iterations": 100
    }
  },
  "point_lookup": {
    "p50_ms": 261.64,
    "p95_ms": 294.18,
    "iterations": 100,
    "method": "direct _key document lookup"
  },
  "indexed_lookup": {
    "p50_ms": 262.4,
    "p95_ms": 304.93,
    "iterations": 100,
    "indexed": true,
    "indexed_field": "person_id (persistent index)"
  },
  "aggregation": {
    "p50_ms": 368.27,
    "p95_ms": 611.15,
    "iterations": 100,
    "query_description": "Top-100 nodes by out-degree (group-by style aggregation)"
  },
  "mixed_workload": {
    "concurrent_clients": 10,
    "duration_sec": 30,
    "read_write_mix": "80/20",
    "total_operations": 1077,
    "queries_per_sec": 35.9
  }
}
```

## Status

**ArangoDB AQL benchmark: ✅ Completed**

All four graph databases have now completed the benchmark phase:

* ✅ CognoDB
* ✅ Memgraph
* ✅ Neo4j Local
* ✅ ArangoDB

The next step is to consolidate the **load performance + query latency + mixed workload throughput** into a final comparison and recommendation.

