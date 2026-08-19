# Neo4j Local Dataset Load

The SNAP soc-Pokec dataset has been successfully loaded into **Neo4j Local**.

## Load Command

```bash
python3 loader_neo4j_local.py
```

## Load Output

```text
=== Loading Neo4j-Local ===
[Neo4j-Local] Connection verified: connected
[Neo4j-Local] Cleared existing data.
[Neo4j-Local] Index created on Person.id
[Neo4j-Local] Loaded 60454 nodes in 7.65s (7901.1 nodes/sec)
[Neo4j-Local] Loaded 120000 relationships in 8.76s (13704.2 rels/sec)
[Neo4j-Local] Post-load check -> nodes: 60454, relationships: 120000
```

## Load Summary

| Metric                 |                         Result |
| ---------------------- | -----------------------------: |
| Platform               |                **Neo4j Local** |
| Nodes Loaded           |                     **60,454** |
| Node Load Time         |                   **7.65 sec** |
| Node Load Rate         |          **7,901.1 nodes/sec** |
| Relationships Loaded   |                    **120,000** |
| Relationship Load Time |                   **8.76 sec** |
| Relationship Load Rate | **13,704.2 relationships/sec** |
| Verified Nodes         |                     **60,454** |
| Verified Relationships |                    **120,000** |

## Verification

Post-load verification confirms that the dataset was successfully loaded:

* ✅ Neo4j connection verified
* ✅ Existing data cleared before loading
* ✅ `Person.id` index created
* ✅ **60,454 nodes** loaded
* ✅ **120,000 relationships** loaded
* ✅ Post-load node count verified
* ✅ Post-load relationship count verified

## Results File

The detailed load results have been saved to:

```text
results/load_result_neo4j_local.json
```

### Result JSON

```json
{
  "platform": "Neo4j-Local",
  "node_count": 60454,
  "node_load_time_sec": 7.65,
  "nodes_per_sec": 7901.1,
  "relationship_count": 120000,
  "relationship_load_time_sec": 8.76,
  "relationships_per_sec": 13704.2,
  "verified_node_count": 60454,
  "verified_relationship_count": 120000
}
```

## Status

**Neo4j Local dataset loading: ✅ Completed**

The same **60,454 nodes and 120,000 relationships** are now loaded and verified in Neo4j Local.

The dataset is ready for the next phase: **benchmark query execution and performance comparison** across:

* CognoDB
* Neo4j Local
* Memgraph Cloud
* ArangoDB Oasis

