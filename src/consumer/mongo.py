import pymongo
from config import MONGO_HOST, MONGO_PASSWORD, MONGO_PORT, MONGO_USERNAME


def get_mongo_client():
    client = pymongo.MongoClient(
        f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin",
        username=MONGO_USERNAME,
        password=MONGO_PASSWORD,
    )
    return client
