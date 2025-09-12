from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

_client = None

def obter_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client