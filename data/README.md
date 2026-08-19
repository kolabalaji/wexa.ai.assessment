# Dataset Preparation

## Dataset Selection

For this assignment, we will use the **SNAP soc-Pokec** dataset.

The alternative would be a smaller/easier dataset, such as a movie/actor graph, if the Pokec dataset feels excessive for the timeline.

Given the time constraints, **SNAP soc-Pokec** is a good choice because:

* It is explicitly mentioned in the assignment.
* It provides additional credibility by using the requested dataset.
* Trimming the dataset to approximately **100k–150k relationships** is straightforward.
* The resulting dataset is small enough for development and testing.

---

## 1. Download the Dataset

Create a directory for the assignment dataset and download the SNAP soc-Pokec relationships file:

```bash
mkdir -p ~/wexai_assignment/data
cd ~/wexai_assignment/data

wget https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz
gunzip soc-pokec-relationships.txt.gz
```

The downloaded file is an **edge list**.

Each line represents a directed relationship:

```text
<from_node_id>	<to_node_id>
```

The full dataset contains approximately **30 million relationships**, which is significantly larger than required for this assignment.

---

## 2. Inspect the Dataset

Check the total number of relationships:

```bash
wc -l soc-pokec-relationships.txt
```

View the first five records:

```bash
head -5 soc-pokec-relationships.txt
```

Example output:

```text
1    2
1    3
1    4
...
```

---

## 3. Trim the Dataset

To keep the dataset manageable, extract approximately **120,000 relationships**.

The simplest approach is to take the first 120,000 lines:

```bash
head -n 120000 soc-pokec-relationships.txt > pokec_trimmed_edges.txt
```

Verify the number of relationships:

```bash
wc -l pokec_trimmed_edges.txt
```

Expected output:

```text
120000 pokec_trimmed_edges.txt
```

For this social graph, taking a prefix of the edge list provides a useful, non-trivial subgraph for development and testing.

---

## 4. Extract Unique Nodes

Extract the source and destination node IDs:

```bash
cut -f1 pokec_trimmed_edges.txt > col1.txt
cut -f2 pokec_trimmed_edges.txt > col2.txt
```

Combine both columns, sort them, and remove duplicates:

```bash
cat col1.txt col2.txt | sort -n | uniq > pokec_trimmed_nodes.txt
```

Check the number of unique nodes:

```bash
wc -l pokec_trimmed_nodes.txt
```

The temporary files can then be removed:

```bash
rm col1.txt col2.txt
```

At this point, we have two clean input files:

```text
pokec_trimmed_nodes.txt
pokec_trimmed_edges.txt
```

### File Formats

**`pokec_trimmed_nodes.txt`**

Contains one node ID per line:

```text
1
2
3
4
5
...
```

**`pokec_trimmed_edges.txt`**

Contains one relationship per line:

```text
from_id    to_id
```

---

## 5. Convert the Dataset to CSV

For consistent parsing by the application/loader scripts, convert the trimmed dataset into CSV format.

Run:

```bash
python3 prepare_dataset.py
```

The resulting files are:

```text
data/
├── nodes.csv
└── edges.csv
```

### `nodes.csv`

Example:

```csv
id
1
2
3
4
5
6
7
8
9
```

### `edges.csv`

Example:

```csv
from_id,to_id
1,13
1,11
1,6
1,3
1,4
1,5
1,15
1,14
1,7
```

---

## 6. Record Dataset Statistics

Once the CSV files have been generated, record the exact number of nodes and relationships.

### Number of Nodes

```bash
echo "Nodes: $(( $(wc -l < data/nodes.csv) - 1 ))"
```

### Number of Relationships

```bash
echo "Relationships: $(( $(wc -l < data/edges.csv) - 1 ))"
```

The `-1` accounts for the CSV header row.

Example:

```text
Nodes: 12345
Relationships: 119999
```

> **Note:** Replace the example node count above with the actual number produced by your dataset preparation script.

---

## Final Dataset Structure

The final project structure should look similar to:

```text
wexa.ai.assessment/
├── data/
│   ├── nodes.csv
│   └── edges.csv
├── prepare_dataset.py
└── ...
```

The dataset is now ready to be consumed by the application/loader.

### Summary

| Item          | Value                     |
| ------------- | ------------------------- |
| Dataset       | SNAP soc-Pokec            |
| Original Size | ~30M relationships        |
| Trimmed Size  | ~120K relationships       |
| Format        | CSV                       |
| Nodes         | Determined after trimming |
| Relationships | ~120K                     |

