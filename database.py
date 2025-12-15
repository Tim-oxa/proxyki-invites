from pymongo import AsyncMongoClient
from config import *


client = AsyncMongoClient(DB_URL)
db = client.get_database(DB_NAME)
