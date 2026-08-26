import csv
import time
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("COGNODB_URI")
user = os.getenv("COGNODB_USER")
password = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def load_users(session):
    print("Loading users...")
    with open("dataset_users.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            batch.append(row)
            if len(batch) >= 500:
                session.run(
                    "UNWIND $rows AS row "
                    "CREATE (u:User {id: toInteger(row.id), name: row.name, city: row.city})",
                    rows=batch
                )
                batch = []
        if batch:
            session.run(
                "UNWIND $rows AS row "
                "CREATE (u:User {id: toInteger(row.id), name: row.name, city: row.city})",
                rows=batch
            )

def create_index(session):
    print("Creating index on User.id...")
    session.run("CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)")

def load_friendships(session):
    print("Loading friendships...")
    with open("dataset_friendships.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            batch.append(row)
            if len(batch) >= 500:
                session.run(
                    "UNWIND $rows AS row "
                    "MATCH (a:User {id: toInteger(row.source_id)}), (b:User {id: toInteger(row.target_id)}) "
                    "CREATE (a)-[:FRIENDS_WITH]->(b)",
                    rows=batch
                )
                batch = []
        if batch:
            session.run(
                "UNWIND $rows AS row "
                "MATCH (a:User {id: toInteger(row.source_id)}), (b:User {id: toInteger(row.target_id)}) "
                "CREATE (a)-[:FRIENDS_WITH]->(b)",
                rows=batch
            )

if __name__ == "__main__":
    start = time.time()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")  # clean slate
        create_index(session)
        load_users(session)
        load_friendships(session)
    elapsed = time.time() - start
    print(f"Done! Total load time: {elapsed:.2f} seconds")
    driver.close()