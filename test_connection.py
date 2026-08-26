from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("COGNODB_URI")
user = os.getenv("COGNODB_USER")
password = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("RETURN 'Hello from CognoDB!' AS message")
    for record in result:
        print(record["message"])

driver.close()