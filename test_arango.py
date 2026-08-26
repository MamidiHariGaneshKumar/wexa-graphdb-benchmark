from arango import ArangoClient
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("ARANGO_URL")
user = os.getenv("ARANGO_USER")
password = os.getenv("ARANGO_PASSWORD")

client = ArangoClient(hosts=url)

sys_db = client.db("_system", username=user, password=password)

print("Connected! Databases available:", sys_db.databases())