from pymongo import MongoClient


def connect_to_mongodb():
    client = MongoClient("mongodb+srv://outman:outman@ol-cluster-rpvwa.mongodb.net/test?retryWrites=true&w=majority")
    database = client.get_database("all")
    collection = database["crawler"]
    return collection


def insert_into_mongodb(data_df):
    collection = connect_to_mongodb()
    data_dict = data_df.to_dict(orient='records')
    collection.insert_many(data_dict)

