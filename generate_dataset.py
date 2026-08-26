import csv
import random
from faker import Faker

fake = Faker()
random.seed(42)  # so results are reproducible

NUM_USERS = 20000
NUM_FRIENDSHIPS = 120000

print("Generating users...")
with open("dataset_users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "city"])
    for i in range(NUM_USERS):
        writer.writerow([i, fake.first_name(), fake.city()])

print("Generating friendships...")
with open("dataset_friendships.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source_id", "target_id"])
    count = 0
    seen = set()
    while count < NUM_FRIENDSHIPS:
        a = random.randint(0, NUM_USERS - 1)
        b = random.randint(0, NUM_USERS - 1)
        if a != b and (a, b) not in seen:
            writer.writerow([a, b])
            seen.add((a, b))
            count += 1
        if count % 20000 == 0:
            print(f"  {count}/{NUM_FRIENDSHIPS} done")

print("Done! Files created: dataset_users.csv, dataset_friendships.csv")