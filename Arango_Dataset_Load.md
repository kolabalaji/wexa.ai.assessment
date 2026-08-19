# ArangoDB Dataset Load

The SNAP soc-Pokec dataset has been successfully loaded into **ArangoDB**.

## Load Command

```bash
python3 loader_arango.py
```

## Load Output

```text
[ArangoDB] CA cert written to cert_file.crt
=== Loading ArangoDB ===
[ArangoDB] Connection verified. Server version: 3.12.10
[ArangoDB] Cleared existing collections.
[ArangoDB] Created 'nodes' (document) and 'edges' (edge) collections.
[ArangoDB] Index created on nodes.person_id
[ArangoDB] Loaded 60454 nodes in 32.90s (1837.8 nodes/sec)
[ArangoDB] Loaded 120000 relationships in 63.05s (1903.4 rels/sec)
[ArangoDB] Post-load check -> nodes: 60454, relationships: 120000
```

> **Note:** ArangoDB reported a deprecation warning for `add_persistent_index()`. The current recommended API is `add_index()` with `type="persistent"`. This warning does not affect the dataset loading process.

## Load Summary

| Metric                 |                        Result |
| ---------------------- | ----------------------------: |
| Platform               |                  **ArangoDB** |
| Server Version         |                   **3.12.10** |
| Nodes Loaded           |                    **60,454** |
| Node Load Time         |                 **32.90 sec** |
| Node Load Rate         |         **1,837.8 nodes/sec** |
| Relationships Loaded   |                   **120,000** |
| Relationship Load Time |                 **63.05 sec** |
| Relationship Load Rate | **1,903.4 relationships/sec** |
| Verified Nodes         |                    **60,454** |
| Verified Relationships |                   **120,000** |

## Database Structure

The following ArangoDB collections were created:

| Collection | Type     | Purpose                            |
| ---------- | -------- | ---------------------------------- |
| `nodes`    | Document | Stores person/node records         |
| `edges`    | Edge     | Stores relationships between nodes |

An index was created on:

```text
nodes.person_id
```

## Verification

Post-load verification confirms that the dataset was successfully loaded:

* ✅ ArangoDB connection verified
* ✅ Server version `3.12.10` verified
* ✅ Existing collections cleared
* ✅ `nodes` document collection created
* ✅ `edges` edge collection created
* ✅ `nodes.person_id` index created
* ✅ **60,454 nodes** loaded
* ✅ **120,000 relationships** loaded
* ✅ Post-load node count verified
* ✅ Post-load relationship count verified

## Results File

The detailed load results have been saved to:

```text
results/load_result_arangodb.json
```

### Result JSON

```json
{
  "platform": "ArangoDB",
  "node_count": 60454,
  "node_load_time_sec": 32.9,
  "nodes_per_sec": 1837.8,
  "relationship_count": 120000,
  "relationship_load_time_sec": 63.05,
  "relationships_per_sec": 1903.4,
  "verified_node_count": 60454,
  "verified_relationship_count": 120000
}
```

## Status

**ArangoDB dataset loading: ✅ Completed**

The same **60,454 nodes and 120,000 relationships** are now loaded and verified in ArangoDB.

The dataset is ready for the next phase: **benchmark query execution and performance comparison** across CognoDB, Neo4j, Memgraph, and ArangoDB.

