# CognoDB Dataset Load

The SNAP soc-Pokec dataset has been successfully loaded into **CognoDB**.

## Load Command

```bash
python3 loader_cognodb.py
```

## Load Output

```text
=== Loading CognoDB ===
[CognoDB] Connection verified: connected
[CognoDB] Cleared existing data.
[CognoDB] Index created on Person.id
[CognoDB] Loaded 60454 nodes in 11.65s (5188.0 nodes/sec)
[CognoDB] Loaded 120000 relationships in 19.56s (6134.3 rels/sec)
[CognoDB] Post-load check -> nodes: 60454, relationships: 120000
```

## Load Summary

| Metric                 |                        Result |
| ---------------------- | ----------------------------: |
| Platform               |                   **CognoDB** |
| Nodes Loaded           |                    **60,454** |
| Node Load Time         |                 **11.65 sec** |
| Node Load Rate         |           **5,188 nodes/sec** |
| Relationships Loaded   |                   **120,000** |
| Relationship Load Time |                 **19.56 sec** |
| Relationship Load Rate | **6,134.3 relationships/sec** |
| Verified Nodes         |                    **60,454** |
| Verified Relationships |                   **120,000** |

### Verification

Post-load verification confirms that the complete dataset was successfully loaded:

* ✅ **60,454 nodes**
* ✅ **120,000 relationships**
* ✅ Connection verified
* ✅ Existing data cleared before loading
* ✅ `Person.id` index created
* ✅ Post-load counts verified

## Results File

The detailed load results have been saved to:

```text
results/load_result_cognodb.json
```

### Result JSON

```json
{
  "platform": "CognoDB",
  "node_count": 60454,
  "node_load_time_sec": 11.65,
  "nodes_per_sec": 5188.0,
  "relationship_count": 120000,
  "relationship_load_time_sec": 19.56,
  "relationships_per_sec": 6134.3,
  "verified_node_count": 60454,
  "verified_relationship_count": 120000
}
```

## Status

**CognoDB dataset loading: ✅ Completed**

The dataset is now ready for the next phase: **benchmark query execution and performance comparison** across CognoDB, Neo4j, Memgraph, and ArangoDB.

