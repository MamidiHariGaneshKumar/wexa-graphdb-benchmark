from run_workloads import run_arango_workloads, results
import csv
import os
from dotenv import load_dotenv

load_dotenv()

print("Running ArangoDB workloads...")
run_arango_workloads(
    os.getenv("ARANGO_URL"),
    os.getenv("ARANGO_USER"),
    os.getenv("ARANGO_PASSWORD")
)

with open("../results/arango_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["database", "workload", "p50_ms", "p95_ms", "iterations"])
    writer.writeheader()
    writer.writerows(results)

print("Done! Saved to results/arango_results.csv")