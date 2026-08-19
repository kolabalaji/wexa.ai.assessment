import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.environ["COGNODB_URI"]
user = os.environ["COGNODB_USER"]
password = os.environ["COGNODB_PASSWORD"]

driver = GraphDatabase.driver(uri, auth=(user, password))

def run_test_query(tx):
    result = tx.run("RETURN 'Hello CognoDB' AS message")
    return result.single()["message"]

with driver.session() as session:
    message = session.execute_read(run_test_query)
    print(message)

driver.close()
