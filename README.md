# wexa.ai.assessment
wexa.ai.assessment


###All 4 platforms###

##Platform	Status##

CognoDB	        ✅ confirmed
Local Neo4j	    ✅ confirmed
Memgraph Cloud	✅ confirmed
ArangoDB Oasis	✅ confirmed 

All 4 comparison databases plus CognoDB are connected. That's the entire infrastructure-setup phase of the assignment done.

###Next step: the dataset###

Downloading and trimming the SNAP soc-Pokec sample to ~100–150k relationships, or
An alternative smaller/easier dataset (like a movie/actor graph) if Pokec feels like overkill for your timeline

mkdir -p ~/wexai_assignment/data
cd ~/wexai_assignment/data

wget https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz
gunzip soc-pokec-relationships.txt.gz



