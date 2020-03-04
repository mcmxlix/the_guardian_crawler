from pymongo import MongoClient


def connect_to_mongodb():
    """ Function to create a connection with MongoDB Atlas """
    client = MongoClient("mongodb+srv://<user>:<password>@ol-cluster-rpvwa.mongodb.net/test?retryWrites=true&w=majority")
    # The name of our database is "all"
    database = client.get_database("all")
    # The name of our collection is "crawler"
    collection = database["crawler"]
    return collection


def insert_into_mongodb(data_df):
    """ Function to send data to MongoDB Atlas """
    collection = connect_to_mongodb()
    # Convert data frame to a dictionary type
    data_dict = data_df.to_dict(orient='records')
    # Insert data frame in our collection
    collection.insert_many(data_dict)

