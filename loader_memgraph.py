"""
loader_memgraph.py

Standalone loader for Memgraph Cloud.
Uses gqlalchemy (the client library that already worked in your test script).

Usage:
    python3 loader_memgraph.py

Requires:
    pip install gqlalchemy python-dotenv

.env must contain:
    MEMGRAPH_HOST=<your memgraph host/IP>
    MEMGRAPH_PORT=7687
    MEMGRAPH_USERNAME=<your username>
    MEMGRAPH_PASSWORD=<your password>

Expects:
    data/nodes.csv  -> header: id
    data/edges.csv  -> header: from_id,to_id

IMPORTANT: never commit real credentials. Keep them in .env only,
and make sure .env is listed in .gitignore.
"""

import os
import csv
import time
import json
from gqlalchemy import Memgraph

BATCH_SIZE = 2000
NODES_CSV = "data/nodes.csv"
EDGES_CSV = "data/edges.csv"


def verify_connection(db):
    results = db.execute_and_fetch("RETURN 'connected' AS status")
    status = next(results)["status"]
    print(f"[Memgraph] Connection verified: {status}")


def clear_database(db):
    db.execute("MATCH (n) DETACH DELETE n")
    print("[Memgraph] Cleared existing data.")


def create_index(db):
    # Needed later for the indexed/filtered lookup benchmark
    db.execute("CREATE INDEX ON :Person(id)")
    print("[Memgraph] Index created on Person.id")


def insert_node_batch(db, batch):
    db.execute(
        """
        UNWIND $batch AS row
        CREATE (:Person {id: row.id})
        """,
        {"batch": batch},
    )


def load_nodes(db, path):
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({"id": int(row["id"])})
            if len(batch) >= BATCH_SIZE:
                insert_node_batch(db, batch)
                total += len(batch)
                batch = []
        if batch:
            insert_node_batch(db, batch)
            total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[Memgraph] Loaded {total} nodes in {elapsed:.2f}s ({rate:.1f} nodes/sec)")
    return total, elapsed


def insert_edge_batch(db, batch):
    db.execute(
        """
        UNWIND $batch AS row
        MATCH (a:Person {id: row.from_id})
        MATCH (b:Person {id: row.to_id})
        CREATE (a)-[:FRIENDS_WITH]->(b)
        """,
        {"batch": batch},
    )


def load_edges(db, path):
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({"from_id": int(row["from_id"]), "to_id": int(row["to_id"])})
            if len(batch) >= BATCH_SIZE:
                insert_edge_batch(db, batch)
                total += len(batch)
                batch = []
        if batch:
            insert_edge_batch(db, batch)
            total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[Memgraph] Loaded {total} relationships in {elapsed:.2f}s ({rate:.1f} rels/sec)")
    return total, elapsed


def sanity_check(db):
    node_count = next(db.execute_and_fetch("MATCH (n) RETURN count(n) AS c"))["c"]
    edge_count = next(db.execute_and_fetch("MATCH ()-[r]->() RETURN count(r) AS c"))["c"]
    print(f"[Memgraph] Post-load check -> nodes: {node_count}, relationships: {edge_count}")
    return node_count, edge_count


def main():
    from dotenv import load_dotenv
    load_dotenv()

    host = os.environ["MEMGRAPH_HOST"]
    port = int(os.environ["MEMGRAPH_PORT"])
    username = os.environ["MEMGRAPH_USERNAME"]
    password = os.environ["MEMGRAPH_PASSWORD"]

    db = Memgraph(host, port, username, password, encrypted=True)

    print("=== Loading Memgraph ===")
    verify_connection(db)
    clear_database(db)
    create_index(db)

    node_count, node_time = load_nodes(db, NODES_CSV)
    edge_count, edge_time = load_edges(db, EDGES_CSV)

    verified_nodes, verified_edges = sanity_check(db)

    result = {
        "platform": "Memgraph",
        "node_count": node_count,
        "node_load_time_sec": round(node_time, 2),
        "nodes_per_sec": round(node_count / node_time, 1) if node_time > 0 else None,
        "relationship_count": edge_count,
        "relationship_load_time_sec": round(edge_time, 2),
        "relationships_per_sec": round(edge_count / edge_time, 1) if edge_time > 0 else None,
        "verified_node_count": verified_nodes,
        "verified_relationship_count": verified_edges,
    }

    print("\n--- Memgraph Load Summary ---")
    print(json.dumps(result, indent=2))

    os.makedirs("results", exist_ok=True)
    out_path = "results/load_result_memgraph.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
