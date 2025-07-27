from pymongo import MongoClient
import os
from fastapi import Depends

client = MongoClient(os.getenv("MONGO_URI"))
db = client.vehicle_monitoring

def get_db():
    return db
