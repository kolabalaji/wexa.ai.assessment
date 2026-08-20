# Final Performance Comparison & Recommendation

All four graph database platforms were tested using the same SNAP soc-Pokec dataset:

* **60,454 nodes**
* **120,000 relationships**

The benchmark covers three major areas:

1. Data loading performance
2. Query latency
3. Mixed read/write workload throughput

---

## 1. Data Loading Performance

### Node Loading

| Platform        |  Nodes |  Load Time |   Nodes/sec |
| --------------- | -----: | ---------: | ----------: |
| **Neo4j Local** | 60,454 | **7.65 s** | **7,901.1** |
| CognoDB         | 60,454 |    11.65 s |     5,188.0 |
| Memgraph        | 60,454 |    19.23 s |     3,143.8 |
| ArangoDB        | 60,454 |    32.90 s |     1,837.8 |

### Relationship Loading

| Platform        | Relationships |  Load Time | Relationships/sec |
| --------------- | ------------: | ---------: | ----------------: |
| **Neo4j Local** |       120,000 | **8.76 s** |      **13,704.2** |
| CognoDB         |       120,000 |    19.56 s |           6,134.3 |
| Memgraph        |       120,000 |    33.76 s |           3,554.4 |
| ArangoDB        |       120,000 |    63.05 s |           1,903.4 |

### Loading Performance Summary

**Neo4j Local was the fastest database for both node and relationship loading.**

```text
Node Loading

Neo4j Local  ████████████████████████████████████  7,901 nodes/sec
CognoDB      ██████████████████████████            5,188 nodes/sec
Memgraph     ████████████████                      3,144 nodes/sec
ArangoDB     █████████                             1,838 nodes/sec
```

```text
Relationship Loading

Neo4j Local  ████████████████████████████████████  13,704 rels/sec
CognoDB      ██████████████████                    6,134 rels/sec
Memgraph     ██████████                            3,554 rels/sec
ArangoDB     █████                                 1,903 rels/sec
```

---

# 2. Query Latency Comparison

The following benchmarks were executed with **100 iterations** per workload.

## P50 Latency

| Query           |   CognoDB |  Memgraph |  Neo4j Local |  ArangoDB |
| --------------- | --------: | --------: | -----------: | --------: |
| 1-Hop Traversal | 235.16 ms | 177.40 ms |  **5.62 ms** | 268.59 ms |
| 2-Hop Traversal | 234.39 ms | 172.45 ms |  **4.52 ms** | 263.78 ms |
| 3-Hop Traversal | 233.51 ms | 175.68 ms |  **6.04 ms** | 261.21 ms |
| Point Lookup    | 235.62 ms | 180.41 ms |  **4.04 ms** | 261.64 ms |
| Aggregation     | 404.81 ms | 224.93 ms | **41.12 ms** | 368.27 ms |

### P95 Latency

| Query           |   CognoDB |  Memgraph |  Neo4j Local |  ArangoDB |
| --------------- | --------: | --------: | -----------: | --------: |
| 1-Hop Traversal | 243.00 ms | 234.15 ms |  **8.88 ms** | 324.48 ms |
| 2-Hop Traversal | 242.60 ms | 175.50 ms |  **7.17 ms** | 325.43 ms |
| 3-Hop Traversal | 238.15 ms | 181.59 ms | **15.01 ms** | 313.13 ms |
| Point Lookup    | 245.30 ms | 184.29 ms |  **6.45 ms** | 294.18 ms |
| Aggregation     | 463.94 ms | 230.56 ms | **67.68 ms** | 611.15 ms |

---

# 3. Mixed Read/Write Throughput

The mixed workload used the same configuration across all platforms:

* **10 concurrent clients**
* **30 seconds**
* **80% reads**
* **20% writes**

| Platform        | Total Operations | Queries/sec |
| --------------- | ---------------: | ----------: |
| **Neo4j Local** |       **31,160** | **1,038.7** |
| Memgraph        |            1,566 |        52.2 |
| CognoDB         |            1,139 |        38.0 |
| ArangoDB        |            1,077 |        35.9 |

### Throughput Comparison

```text
Neo4j Local  ████████████████████████████████████  1,038.7 QPS
Memgraph     ██                                      52.2 QPS
CognoDB      ██                                      38.0 QPS
ArangoDB     █                                       35.9 QPS
```

Neo4j Local achieved approximately **20x the throughput of Memgraph** and substantially higher throughput than CognoDB and ArangoDB in this specific benchmark environment.

---

# 4. Overall Comparison

| Category             | CognoDB | Memgraph | Neo4j Local | ArangoDB |
| -------------------- | :-----: | :------: | :---------: | :------: |
| Node Loading         |    🥈   |    🥉    |      🥇     |    4th   |
| Relationship Loading |    🥈   |    🥉    |      🥇     |    4th   |
| 1-Hop Latency        |    🥈   |    🥈    |      🥇     |    4th   |
| 2-Hop Latency        |    🥈   |    🥈    |      🥇     |    4th   |
| 3-Hop Latency        |    🥈   |    🥈    |      🥇     |    4th   |
| Point Lookup         |    🥈   |    🥈    |      🥇     |    4th   |
| Aggregation          |   3rd   |    🥈    |      🥇     |    4th   |
| Mixed Workload       |    🥈   |    🥈    |      🥇     |    4th   |

> The rankings above are based strictly on the measured benchmark results and should not be interpreted as general product rankings.

---

# 5. Final Recommendation

## 🥇 Neo4j Local — Best Overall Performance

Based on the collected benchmark results, **Neo4j Local is the clear performance leader for this workload**.

It achieved:

* Fastest node loading: **7,901.1 nodes/sec**
* Fastest relationship loading: **13,704.2 relationships/sec**
* Lowest P50 latency across every tested read workload
* Lowest P95 latency across every tested read workload
* Highest aggregation performance
* Highest mixed workload throughput: **1,038.7 QPS**

The results indicate that Neo4j is particularly well suited to this graph traversal and mixed read/write workload.

---

## 🥈 Memgraph — Strong Alternative

Memgraph delivered the second-best overall query performance among the tested systems.

Its strengths include:

* Better traversal latency than CognoDB and ArangoDB
* Strong aggregation performance
* Higher mixed-workload throughput than CognoDB and ArangoDB

However, its loading performance and query latency were significantly behind Neo4j Local in this test environment.

---

## 🥉 CognoDB — Promising Baseline

CognoDB successfully handled the complete dataset and benchmark suite.

It achieved:

* **5,188 nodes/sec** during loading
* **6,134 relationships/sec** during loading
* Consistent traversal latency
* **38.0 QPS** under the mixed workload

The results establish a useful baseline for CognoDB and provide clear opportunities for future optimization, particularly around query latency and concurrent workload throughput.

---

## ArangoDB — Functional but Slower for This Workload

ArangoDB successfully completed both data loading and AQL benchmarking.

However, it recorded the slowest loading performance and relatively high query latency for the tested workloads.

Its mixed workload throughput was:

```text
35.9 QPS
```

The aggregation P95 was also relatively high at:

```text
611.15 ms
```

For this particular graph workload, ArangoDB did not match the performance of the other tested platforms.

---

# 6. Final Ranking

Based on the complete benchmark:

|     Rank | Platform        | Overall Assessment                              |
| -------: | --------------- | ----------------------------------------------- |
| 🥇 **1** | **Neo4j Local** | Best overall performance                        |
| 🥈 **2** | **Memgraph**    | Strong graph query performance                  |
| 🥉 **3** | **CognoDB**     | Functional baseline with optimization potential |
|    **4** | **ArangoDB**    | Functional but slower for this workload         |

---

# 7. Important Benchmark Disclaimer

These results should be interpreted within the context of this specific benchmark environment.

Performance can vary significantly depending on:

* Hardware resources
* CPU and memory allocation
* Database configuration
* Database version
* Network latency
* Cloud vs. local deployment
* Query implementation
* Index configuration
* Dataset size and graph topology
* Concurrency level
* Cache/warm-up state

In particular, **Neo4j was tested locally**, while Memgraph and ArangoDB were deployed remotely/cloud-based. Therefore, the results are useful for this assignment and workload comparison, but they should not be treated as a controlled apples-to-apples infrastructure benchmark.

---

# 8. Conclusion

All four graph databases successfully loaded and queried the same **60,454-node / 120,000-relationship** dataset.

The benchmark results show a clear performance advantage for **Neo4j Local** across loading speed, query latency, and mixed workload throughput.

For the workload tested in this assignment:

> **Neo4j Local provides the best overall performance, while Memgraph provides the strongest alternative among the other evaluated platforms. CognoDB establishes a functional baseline with opportunities for further performance optimization, and ArangoDB performs adequately but is slower for this particular workload.**

---

## Benchmark Artifacts

The raw benchmark results are available in:

```text
results/
├── load_result_cognodb.json
├── load_result_memgraph.json
├── load_result_neo4j_local.json
├── load_result_arangodb.json
├── benchmark_results_cypher.json
└── benchmark_results_arangodb.json
```

### Benchmark Status

* [x] Dataset prepared
* [x] CognoDB loaded
* [x] Memgraph loaded
* [x] Neo4j Local loaded
* [x] ArangoDB loaded
* [x] Cypher benchmarks completed
* [x] ArangoDB AQL benchmarks completed
* [x] Load performance compared
* [x] Query latency compared
* [x] Mixed workload throughput compared
* [x] Final recommendation completed

