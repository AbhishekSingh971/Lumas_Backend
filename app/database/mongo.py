from flask import current_app
from pymongo import MongoClient

_client = None

def init_mongo(app):
    global _client
    _client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=5000)
    app.extensions["mongo_client"] = _client

def get_db():
    client = current_app.extensions["mongo_client"]
    return client[current_app.config["MONGO_DB_NAME"]]
