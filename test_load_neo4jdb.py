import os
from neo4j import GraphDatabase


uri = "bolt://localhost:7687"
user = "neo4j"
password = 'Balaji@123'

driver = GraphDatabase.driver(uri, auth=(user, password))

def load_test_data(tx):
    tx.run("""
        CREATE (a:Person {id: 1, name: 'Alice'})
        CREATE (b:Person {id: 2, name: 'Bob'})
        CREATE (c:Person {id: 3, name: 'Carol'})
        CREATE (a)-[:FRIENDS_WITH]->(b)
        CREATE (b)-[:FRIENDS_WITH]->(c)
        CREATE (a)-[:FRIENDS_WITH]->(c)
    """)

with driver.session() as session:
    session.execute_write(load_test_data)
    print("Test data loaded.")

driver.close()
