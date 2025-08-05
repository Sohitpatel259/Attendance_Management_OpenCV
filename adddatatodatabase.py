import certifi
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

ca = certifi.where()
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI, tlsCAFile=ca)

for db in client.list_database_names():
    print(db)

