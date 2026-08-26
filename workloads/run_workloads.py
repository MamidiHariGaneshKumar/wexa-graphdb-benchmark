import time
import random
import csv
import statistics
from neo4j import GraphDatabase
from arango import ArangoClient
from dotenv import load_dotenv
import os

load_dotenv()
random.seed(42)
ITERATIONS = 100
SAMPLE_IDS = random.sample(range(20000), ITERATIONS)

results = []

def record(db_name, workload, latencies):
    latencies_ms = [l * 1000 for l in latencies]
    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=20)[18]  # 95th percentile
    results.append({
        "database": db_name,
        "workload": workload,
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "iterations": len(latencies)
    })
    print(f"{db_name} | {workload} | p50={p50:.2f}ms | p95={p95:.2f}ms")

# ---------- Cypher-based (CognoDB, Neo4j) ----------
def run_cypher_workloads(db_name, uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:

        # 1-hop traversal
        latencies = []
        for uid in SAMPLE_IDS:
            start = time.time()
            session.run(
                "MATCH (u:User {id: $id})-[:FRIENDS_WITH]->(f) RETURN f LIMIT 50",
                id=uid
            ).consume()
            latencies.append(time.time() - start)
        record(db_name, "1-hop traversal", latencies)

        # 2-hop traversal
        latencies = []
        for uid in SAMPLE_IDS:
            start = time.time()
            session.run(
                "MATCH (u:User {id: $id})-[:FRIENDS_WITH*2]->(f) RETURN DISTINCT f LIMIT 50",
                id=uid
            ).consume()
            latencies.append(time.time() - start)
        record(db_name, "2-hop traversal", latencies)

        # Point lookup
        latencies = []
        for uid in SAMPLE_IDS:
            start = time.time()
            session.run("MATCH (u:User {id: $id}) RETURN u", id=uid).consume()
            latencies.append(time.time() - start)
        record(db_name, "point lookup", latencies)

        # Aggregation
        latencies = []
        for _ in range(ITERATIONS):
            start = time.time()
            session.run(
                "MATCH (u:User) RETURN u.city AS city, count(*) AS cnt ORDER BY cnt DESC LIMIT 10"
            ).consume()
            latencies.append(time.time() - start)
        record(db_name, "aggregation (group by city)", latencies)

    driver.close()

# ---------- AQL-based (ArangoDB) ----------
# ---------- AQL-based (ArangoDB) ----------
def run_arango_workloads(url, user, password):
    client = ArangoClient(hosts=url)
    db = client.db("wexa_benchmark", username=user, password=password)

    # 1-hop traversal
    latencies = []
    for uid in SAMPLE_IDS:
        start = time.time()
        list(db.aql.execute(
            "WITH users FOR v IN 1..1 OUTBOUND @start friendships LIMIT 50 RETURN v",
            bind_vars={"start": f"users/{uid}"}
        ))
        latencies.append(time.time() - start)
    record("ArangoDB", "1-hop traversal", latencies)

    # 2-hop traversal
    latencies = []
    for uid in SAMPLE_IDS:
        start = time.time()
        list(db.aql.execute(
            "WITH users FOR v IN 2..2 OUTBOUND @start friendships LIMIT 50 RETURN DISTINCT v",
            bind_vars={"start": f"users/{uid}"}
        ))
        latencies.append(time.time() - start)
    record("ArangoDB", "2-hop traversal", latencies)

    # Point lookup
    latencies = []
    for uid in SAMPLE_IDS:
        start = time.time()
        list(db.aql.execute(
            "FOR u IN users FILTER u.user_id == @id RETURN u",
            bind_vars={"id": uid}
        ))
        latencies.append(time.time() - start)
    record("ArangoDB", "point lookup", latencies)

    # Aggregation
    latencies = []
    for _ in range(ITERATIONS):
        start = time.time()
        list(db.aql.execute(
            "FOR u IN users COLLECT city = u.city WITH COUNT INTO cnt SORT cnt DESC LIMIT 10 RETURN {city, cnt}"
        ))
        latencies.append(time.time() - start)
    record("ArangoDB", "aggregation (group by city)", latencies)