import csv
import time
from arango import ArangoClient
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("ARANGO_URL")
user = os.getenv("ARANGO_USER")
password = os.getenv("ARANGO_PASSWORD")

client = ArangoClient(hosts=url)
sys_db = client.db("_system", username=user, password=password)

DB_NAME = "wexa_benchmark"

# Create the benchmark database if it doesn't exist
if not sys_db.has_database(DB_NAME):
    sys_db.create_database(DB_NAME)

db = client.db(DB_NAME, username=user, password=password)

def setup_collections():
    if db.has_collection("users"):
        db.delete_collection("users")
    if db.has_collection("friendships"):
        db.delete_collection("friendships")
    db.create_collection("users")
    db.create_collection("friendships", edge=True)
    db.collection("users").add_persistent_index(fields=["user_id"])

def load_users():
    print("Loading users...")
    users_col = db.collection("users")
    batch = []
    with open("dataset_users.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                "_key": row["id"],
                "user_id": int(row["id"]),
                "name": row["name"],
                "city": row["city"]
            })
            if len(batch) >= 500:
                users_col.insert_many(batch)
                batch = []
        if batch:
            users_col.insert_many(batch)

def load_friendships():
    print("Loading friendships...")
    friendships_col = db.collection("friendships")
    batch = []
    with open("dataset_friendships.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append({
                "_from": f"users/{row['source_id']}",
                "_to": f"users/{row['target_id']}"
            })
            if len(batch) >= 500:
                friendships_col.insert_many(batch)
                batch = []
        if batch:
            friendships_col.insert_many(batch)

if __name__ == "__main__":
    start = time.time()
    setup_collections()
    load_users()
    load_friendships()
    elapsed = time.time() - start
    print(f"Done! Total load time: {elapsed:.2f} seconds")