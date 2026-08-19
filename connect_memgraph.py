from gqlalchemy import Memgraph

MEMGRAPH_HOST = '35.159.238.162'
MEMGRAPH_PORT = 7687
MEMGRAPH_USERNAME = 'balaji.kola@gmail.com'
# Place your Memgraph password that was created during Project creation
MEMGRAPH_PASSWORD = 'Shreejan@123'

def hello_memgraph(host: str, port: int, username: str, password: str):
    connection = Memgraph(host, port, username, password, encrypted=True)
    results = connection.execute_and_fetch(
        'CREATE (n:FirstNode { message: "Hello Memgraph from Python!" }) RETURN n.message AS message'
    )
    print("Created node with message:", next(results)["message"])

if __name__ == "__main__":
    hello_memgraph(MEMGRAPH_HOST, MEMGRAPH_PORT, MEMGRAPH_USERNAME, MEMGRAPH_PASSWORD)
