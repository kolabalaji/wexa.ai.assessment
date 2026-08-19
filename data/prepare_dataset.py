# prepare_dataset.py
import csv

with open("pokec_trimmed_nodes.txt") as f, open("nodes.csv", "w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["id"])
    for line in f:
        node_id = line.strip()
        if node_id:
            writer.writerow([node_id])

with open("pokec_trimmed_edges.txt") as f, open("edges.csv", "w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["from_id", "to_id"])
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            writer.writerow(parts)

print("Done. Wrote data/nodes.csv and data/edges.csv")
