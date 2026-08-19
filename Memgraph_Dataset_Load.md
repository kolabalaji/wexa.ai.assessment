# Memgraph Dataset Load

The SNAP soc-Pokec dataset has been successfully loaded into **Memgraph**.

## Load Command

```bash
python3 loader_memgraph.py
```

## Load Output

```text
=== Loading Memgraph ===
[Memgraph] Connection verified: connected
[Memgraph] Cleared existing data.
[Memgraph] Index created on Person.id
[Memgraph] Loaded 60454 nodes in 19.23s (3143.8 nodes/sec)
[Memgraph] Loaded 120000 relationships in 33.76s (3554.4 rels/sec)
[Memgraph] Post-load check -> nodes: 60454, relationships: 120000
```

## Load Summary

| Metric                 |                        Result |
| ---------------------- | ----------------------------: |
| Platform               |                  **Memgraph** |
| Nodes Loaded           |                    **60,454** |
| Node Load Time         |                 **19.23 sec** |
| Node Load Rate         |         **3,143.8 nodes/sec** |
| Relationships Loaded   |                   **120,000** |
| Relationship Load Time |                 **33.76 sec** |
| Relationship Load Rate | **3,554.4 relationships/sec** |
| Verified Nodes         |                    **60,454** |
| Verified Relationships |                   **120,000** |

## Verification

Post-load verification confirms that the dataset was successfully loaded:

* ✅ Memgraph connection verified
* ✅ Existing data cleared before loading
* ✅ `Person.id` index created
* ✅ **60,454 nodes** loaded
* ✅ **120,000 relationships** loaded
* ✅ Post-load node count verified
* ✅ Post-load relationship count verified

## Results File

The detailed load results have been saved to:

```text
results/load_result_memgraph.json
```

### Result JSON

```json
{
  "platform": "Memgraph",
  "node_count": 60454,
  "node_load_time_sec": 19.23,
  "nodes_per_sec": 3143.8,
  "relationship_count": 120000,
  "relationship_load_time_sec": 33.76,
  "relationships_per_sec": 3554.4,
  "verified_node_count": 60454,
  "verified_relationship_count": 120000
}
```

## Status

**Memgraph dataset loading: ✅ Completed**

The same **60,454 nodes and 120,000 relationships** are now loaded and verified in Memgraph.

The dataset is ready for the next phase: **benchmark query execution and performance comparison** across CognoDB, Neo4j, Memgraph, and ArangoDB.

