The dataset


Downloading and trimming the SNAP soc-Pokec sample to ~100–150k relationships, or
An alternative smaller/easier dataset (like a movie/actor graph) if Pokec feels like overkill for your timeline


Given your time crunch, I'll go with SNAP soc-Pokec — it's explicitly named in the assignment (extra credibility points), and trimming it down is actually simpler than sourcing and cleaning a movie/actor dataset from scratch.


1. Download the dataset

mkdir -p ~/wexai_assignment/data
cd ~/wexai_assignment/data

wget https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz
gunzip soc-pokec-relationships.txt.gz


This file is an edge list — each line is <from_node_id>\t<to_node_id>, representing a directed friendship relationship. The full dataset has ~30M relationships, way more than you need.

2. Check what you're working with

wc -l soc-pokec-relationships.txt
head -5 soc-pokec-relationships.txt


You'll see something like:

1    2
1    3
1    4

3. Trim it down to ~100k–150k relationships

The simplest safe approach: take the first N lines, then figure out how many unique nodes that pulls in (don't worry — for a social graph like this, taking a prefix naturally pulls in a connected, non-trivial subgraph)

head -n 120000 soc-pokec-relationships.txt > pokec_trimmed_edges.txt
wc -l pokec_trimmed_edges.txt


4. Extract the unique node list from your trimmed edges

cut -f1 pokec_trimmed_edges.txt > col1.txt
cut -f2 pokec_trimmed_edges.txt > col2.txt
cat col1.txt col2.txt | sort -n | uniq > pokec_trimmed_nodes.txt
wc -l pokec_trimmed_nodes.txt
rm col1.txt col2.txt


This gives you two clean files:

pokec_trimmed_nodes.txt — one node ID per line
pokec_trimmed_edges.txt — one from_id \t to_id relationship per line


5. Convert to CSV (easier for your loader scripts to parse consistently)

prepare_dataset.py 

python3 prepare_dataset.py

6. Record the exact numbers for your README now

echo "Nodes: $(( $(wc -l < data/nodes.csv) - 1 ))"
echo "Relationships: $(( $(wc -l < data/edges.csv) - 1 ))"

e.g:
$ head nodes.csv
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
(venv) balaji@Balaji:~/wexai_assignment/wexa.ai.assessment/data$ head edges.csv
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
