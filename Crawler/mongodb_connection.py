from pymongo import MongoClient
import yaml


def read_yaml():
    """ Function to read parameters from YAML file"""
    with open('../parameters.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data['url_connection'], data['database_name'], data['collection_name']


def connect_to_mongodb(url_connection):
    """ Function to create a connection with MongoDB Atlas """
    client = MongoClient(url_connection)
    return client


def mongodb_db_collection(client, database_name, collection_name):
    """ Function to get collection from database"""
    # The name of our database is "all"
    database = client.get_database(database_name)
    # The name of our collection is "crawler"
    collection = database[collection_name]
    return collection


def insert_into_mongodb(data_df):
    """ Function to send data to MongoDB Atlas """
    url_connection, database_name, collection_name = read_yaml()
    client = connect_to_mongodb(url_connection)
    collection = mongodb_db_collection(client, database_name, collection_name)
    # Convert data frame to a dictionary type
    data_dict = data_df.to_dict(orient='records')
    # Insert data frame in our collection
    collection.insert_many(data_dict)

