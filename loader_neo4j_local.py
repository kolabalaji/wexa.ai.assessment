"""
loader_neo4j_local.py

Standalone loader for a locally-hosted Neo4j instance (Docker or native),
resource-capped to match CognoDB's free tier for fair comparison.

Usage:
    python3 loader_neo4j_local.py

Requires:
    pip install neo4j python-dotenv

.env must contain:
    LOCAL_NEO4J_URI=bolt://localhost:7687
    LOCAL_NEO4J_USER=neo4j
    LOCAL_NEO4J_PASSWORD=<your local password>

Expects:
    data/nodes.csv  -> header: id
    data/edges.csv  -> header: from_id,to_id
"""

import os
import csv
import time
import json
from neo4j import GraphDatabase

BATCH_SIZE = 2000
NODES_CSV = "data/nodes.csv"
EDGES_CSV = "data/edges.csv"


def verify_connection(driver):
    with driver.session() as session:
        status = session.run("RETURN 'connected' AS status").single()["status"]
        print(f"[Neo4j-Local] Connection verified: {status}")


def clear_database(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("[Neo4j-Local] Cleared existing data.")


def create_index(driver):
    with driver.session() as session:
        # Needed later for the indexed/filtered lookup benchmark
        session.run("CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)")
    print("[Neo4j-Local] Index created on Person.id")


def insert_node_batch(session, batch):
    session.run(
        """
        UNWIND $batch AS row
        CREATE (:Person {id: row.id})
        """,
        batch=batch,
    )


def load_nodes(driver, path):
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        with driver.session() as session:
            for row in reader:
                batch.append({"id": int(row["id"])})
                if len(batch) >= BATCH_SIZE:
                    insert_node_batch(session, batch)
                    total += len(batch)
                    batch = []
            if batch:
                insert_node_batch(session, batch)
                total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[Neo4j-Local] Loaded {total} nodes in {elapsed:.2f}s ({rate:.1f} nodes/sec)")
    return total, elapsed


def insert_edge_batch(session, batch):
    session.run(
        """
        UNWIND $batch AS row
        MATCH (a:Person {id: row.from_id})
        MATCH (b:Person {id: row.to_id})
        CREATE (a)-[:FRIENDS_WITH]->(b)
        """,
        batch=batch,
    )


def load_edges(driver, path):
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        with driver.session() as session:
            for row in reader:
                batch.append({"from_id": int(row["from_id"]), "to_id": int(row["to_id"])})
                if len(batch) >= BATCH_SIZE:
                    insert_edge_batch(session, batch)
                    total += len(batch)
                    batch = []
            if batch:
                insert_edge_batch(session, batch)
                total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[Neo4j-Local] Loaded {total} relationships in {elapsed:.2f}s ({rate:.1f} rels/sec)")
    return total, elapsed


def sanity_check(driver):
    with driver.session() as session:
        node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        edge_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    print(f"[Neo4j-Local] Post-load check -> nodes: {node_count}, relationships: {edge_count}")
    return node_count, edge_count


def main():
    from dotenv import load_dotenv
    load_dotenv()

    uri = os.environ["LOCAL_NEO4J_URI"]
    user = os.environ["LOCAL_NEO4J_USER"]
    password = os.environ["LOCAL_NEO4J_PASSWORD"]

    driver = GraphDatabase.driver(uri, auth=(user, password))

    print("=== Loading Neo4j-Local ===")
    verify_connection(driver)
    clear_database(driver)
    create_index(driver)

    node_count, node_time = load_nodes(driver, NODES_CSV)
    edge_count, edge_time = load_edges(driver, EDGES_CSV)

    verified_nodes, verified_edges = sanity_check(driver)

    driver.close()

    result = {
        "platform": "Neo4j-Local",
        "node_count": node_count,
        "node_load_time_sec": round(node_time, 2),
        "nodes_per_sec": round(node_count / node_time, 1) if node_time > 0 else None,
        "relationship_count": edge_count,
        "relationship_load_time_sec": round(edge_time, 2),
        "relationships_per_sec": round(edge_count / edge_time, 1) if edge_time > 0 else None,
        "verified_node_count": verified_nodes,
        "verified_relationship_count": verified_edges,
    }

    print("\n--- Neo4j-Local Load Summary ---")
    print(json.dumps(result, indent=2))

    os.makedirs("results", exist_ok=True)
    out_path = "results/load_result_neo4j_local.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
