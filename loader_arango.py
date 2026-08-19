"""
loader_arango.py

Standalone loader for ArangoDB Oasis.
Uses python-arango (the client library that already worked in your test script).

Usage:
    python3 loader_arango.py

Requires:
    pip install python-arango python-dotenv

.env must contain:
    ARANGO_HOST=https://<your-deployment-id>.arangodb.cloud:18529
    ARANGO_USER=root
    ARANGO_PASSWORD=<your password>
    ARANGO_DB=_system
    ARANGO_CA_B64=<the base64-encoded CA cert string from your Oasis dashboard>

Expects:
    data/nodes.csv  -> header: id
    data/edges.csv  -> header: from_id,to_id

IMPORTANT: never commit real credentials or the decoded cert_file.crt.
Keep them in .env only, and make sure .env and cert_file.crt are both
listed in .gitignore.
"""

import os
import csv
import time
import json
import base64
from arango import ArangoClient

BATCH_SIZE = 2000
NODES_CSV = "data/nodes.csv"
EDGES_CSV = "data/edges.csv"
CERT_PATH = "cert_file.crt"


def write_ca_cert(encoded_ca, path=CERT_PATH):
    """Decodes the base64 CA cert from .env and writes it to disk,
    same as the pattern from the Oasis dashboard's sample code."""
    try:
        file_content = base64.b64decode(encoded_ca)
        with open(path, "w+") as f:
            f.write(file_content.decode("utf-8"))
        print(f"[ArangoDB] CA cert written to {path}")
    except Exception as e:
        print(f"[ArangoDB] Failed to write CA cert: {e}")
        raise


def verify_connection(db):
    version = db.version()
    print(f"[ArangoDB] Connection verified. Server version: {version}")


def clear_collections(db):
    for name in ("nodes", "edges"):
        if db.has_collection(name):
            db.delete_collection(name)
    print("[ArangoDB] Cleared existing collections.")


def create_collections(db):
    db.create_collection("nodes")
    db.create_collection("edges", edge=True)
    print("[ArangoDB] Created 'nodes' (document) and 'edges' (edge) collections.")


def create_index(db):
    nodes = db.collection("nodes")
    # persistent index on person_id -- needed later for the indexed-lookup benchmark
    nodes.add_persistent_index(fields=["person_id"], unique=True)
    print("[ArangoDB] Index created on nodes.person_id")


def load_nodes(db, path):
    nodes = db.collection("nodes")
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row["id"])
            batch.append({"_key": str(node_id), "person_id": node_id})
            if len(batch) >= BATCH_SIZE:
                nodes.insert_many(batch)
                total += len(batch)
                batch = []
        if batch:
            nodes.insert_many(batch)
            total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[ArangoDB] Loaded {total} nodes in {elapsed:.2f}s ({rate:.1f} nodes/sec)")
    return total, elapsed


def load_edges(db, path):
    edges = db.collection("edges")
    batch = []
    total = 0
    start = time.time()
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_id = row["from_id"]
            to_id = row["to_id"]
            batch.append({
                "_from": f"nodes/{from_id}",
                "_to": f"nodes/{to_id}",
            })
            if len(batch) >= BATCH_SIZE:
                edges.insert_many(batch)
                total += len(batch)
                batch = []
        if batch:
            edges.insert_many(batch)
            total += len(batch)
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0
    print(f"[ArangoDB] Loaded {total} relationships in {elapsed:.2f}s ({rate:.1f} rels/sec)")
    return total, elapsed


def sanity_check(db):
    node_count = db.collection("nodes").count()
    edge_count = db.collection("edges").count()
    print(f"[ArangoDB] Post-load check -> nodes: {node_count}, relationships: {edge_count}")
    return node_count, edge_count


def main():
    from dotenv import load_dotenv
    load_dotenv()

    host = os.environ["ARANGO_HOST"]
    user = os.environ["ARANGO_USER"]
    password = os.environ["ARANGO_PASSWORD"]
    db_name = os.environ["ARANGO_DB"]
    encoded_ca = os.environ["ARANGO_CA_B64"]

    write_ca_cert(encoded_ca)

    client = ArangoClient(hosts=host, verify_override=CERT_PATH)
    db = client.db(db_name, username=user, password=password)

    print("=== Loading ArangoDB ===")
    verify_connection(db)
    clear_collections(db)
    create_collections(db)
    create_index(db)

    node_count, node_time = load_nodes(db, NODES_CSV)
    edge_count, edge_time = load_edges(db, EDGES_CSV)

    verified_nodes, verified_edges = sanity_check(db)

    result = {
        "platform": "ArangoDB",
        "node_count": node_count,
        "node_load_time_sec": round(node_time, 2),
        "nodes_per_sec": round(node_count / node_time, 1) if node_time > 0 else None,
        "relationship_count": edge_count,
        "relationship_load_time_sec": round(edge_time, 2),
        "relationships_per_sec": round(edge_count / edge_time, 1) if edge_time > 0 else None,
        "verified_node_count": verified_nodes,
        "verified_relationship_count": verified_edges,
    }

    print("\n--- ArangoDB Load Summary ---")
    print(json.dumps(result, indent=2))

    os.makedirs("results", exist_ok=True)
    out_path = "results/load_result_arangodb.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()
