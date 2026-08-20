# wexa.ai.assessment

## Infrastructure Setup

All **4 comparison platforms + CognoDB** are successfully connected.

| Platform           |    Status   |
| ------------------ | :---------: |
| **CognoDB**        | ✅ Confirmed |
| **Local Neo4j**    | ✅ Confirmed |
| **Memgraph Cloud** | ✅ Confirmed |
| **ArangoDB Oasis** | ✅ Confirmed |

> **Status:** The entire infrastructure setup phase of the assignment is complete. 🎉

---

## Next Step: Dataset

The next step is to prepare a graph dataset for benchmarking and comparison.

### Dataset Options

We can use one of the following approaches:

1. **SNAP soc-Pokec** — Download and trim the dataset to approximately **100k–150k relationships**.
2. **Alternative smaller dataset** — Use an easier dataset, such as a **movie/actor graph**, if SNAP soc-Pokec is too large for the available timeline.

### Recommended Approach

Use **SNAP soc-Pokec** because:

* It is explicitly mentioned in the assignment.
* It provides a realistic social-network graph.
* It avoids the need to source and clean a different dataset.
* The dataset can be easily trimmed to the required size.

---

## Download SNAP soc-Pokec

Create the dataset directory:

```bash
mkdir -p ~/wexai_assignment/data
cd ~/wexai_assignment/data
```

Download the dataset:

```bash
wget https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz
```

Extract the compressed file:

```bash
gunzip soc-pokec-relationships.txt.gz
```

The resulting file will be:

```text
soc-pokec-relationships.txt
```

---

## Dataset Preparation

The original SNAP soc-Pokec dataset contains approximately **30 million relationships**, which is larger than required for this assignment.

The next step is to trim the dataset to approximately **100k–150k relationships** and generate the required node and edge files.

Expected structure:

```text
wexa.ai.assessment/
├── data/
│   ├── nodes.csv
│   └── edges.csv
├── prepare_dataset.py
└── ...
```

### Target Dataset Size

| Metric        |                    Target |
| ------------- | ------------------------: |
| Relationships |                ~100k–150k |
| Nodes         | Determined after trimming |
| Format        |                       CSV |
| Dataset       |            SNAP soc-Pokec |

---

## Current Progress

* [x] CognoDB connected
* [x] Local Neo4j connected
* [x] Memgraph Cloud connected
* [x] ArangoDB Oasis connected
* [x] Infrastructure setup completed
* [x] Download SNAP soc-Pokec
* [x] Trim dataset
* [x] Generate `nodes.csv`
* [x] Generate `edges.csv`
* [x] Load dataset into all platforms
* [x] Run benchmark queries
* [x] Compare performance
* [x] Document results

