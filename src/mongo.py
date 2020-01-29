from pymongo import MongoClient


class Mongo(object):
    def __init__(self, database, host, port):
        client = MongoClient(host, port)
        self.database = client[database]

    def insert_collection(self, collection, data):
        collection = self.database[collection]
        collection.insert_one(data)
