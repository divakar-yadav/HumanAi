import pymongo

def connect_to_mongodb(collection_name):
    mongo_uri = "mongodb://localhost:27017/"
    database_name = "HumanAi"
    client = pymongo.MongoClient(mongo_uri)
    database = client[database_name]
    collection = database[collection_name]
    return collection

def fetch_data_from_mongodb(collection_name):
    collection = connect_to_mongodb(collection_name)
    data = collection.find()
    return list(data)

def save_data_to_mongodb(data,collection_name):
    collection = connect_to_mongodb(collection_name)
    collection.insert_one(data)
