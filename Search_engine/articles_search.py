import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from Crawler.mongodb_connection import mongodb_db_collection, connect_to_mongodb, read_yaml


def train_tfidf_vectorizer(data_frame):
    """
    In this function we will use a TF-IDF vectorizer, that will produce vectors of words for each article's clean text
    with a numeric value that represent the importance of the word, which is related to his frequency in a given 'clean
    text' and the times it was quoted into all 'clean text'
    """
    clean_text = data_frame.clean_text
    # Fit the vectorizer to our training data (clean_text)
    # It will initialize the parameters of the vectorizer
    vectorizer = TfidfVectorizer()
    vectorizer.fit(clean_text)
    # Fit the current data (clean_text) in the model and we transform it
    vect_clean_text = TfidfVectorizer().fit_transform(clean_text)
    return vect_clean_text.toarray(), vectorizer


def articles_parser(data_frame, vect_clean_text, vectorizer, key_words):
    """
    This function will be responsible for adapting our keywords to the tf-idf vectorizer and comparing its
    similarity to all the vectors of the 'vect_clean_text' using 'cosine similarity'
    It will returns the indexes of articles that matches the keywords
    """
    indexes = []
    # Transform our key words to vectors
    vect_key_words = vectorizer.transform([key_words])
    # Calculate similarity between vectors from 'vect_clean_text' and 'vect_key_words'
    cosine_similarities = linear_kernel(vect_key_words, vect_clean_text).flatten()
    # Sort indexes of cosine similarity values
    sorted_indexes = sorted(range(len(cosine_similarities)), key=lambda i: cosine_similarities[i], reverse=True)
    # Get the indexes of values where cosine similarity is greater than the threshold 0.1
    # In other cases, we can directly select the top sorted indexes, but with this loop, we ensure the correspondence..
    # .. between the keywords and the articles
    for i in sorted_indexes:
        if cosine_similarities[i] > 0.1:
            indexes.append(data_frame._id[i])
    return indexes


def articles_search(key_words):
    """ This function returns the articles that best match the keywords  """
    results = []
    # Establish a connection to MongoDB Atlas
    url_connection, database_name, collection_name = read_yaml()
    client = connect_to_mongodb(url_connection)
    collection = mongodb_db_collection(client, database_name, collection_name)
    # Get clean text of articles from MongoDB Atlas to compare it to our keywords
    coll_clean_text = collection.find({}, {"_id": 1, "clean_text": 1})

    coll_clean_text_df = pd.DataFrame(columns=['_id', 'clean_text'])
    for x in coll_clean_text:
        coll_clean_text_df.loc[len(coll_clean_text_df), :] = [x['_id'], x['clean_text']]
    # Call the function 'train_tfidf_vectorizer'
    vect_clean_text, vectorizer = train_tfidf_vectorizer(coll_clean_text_df)
    # Call the function 'articles_parser'
    indexes = articles_parser(coll_clean_text_df, vect_clean_text, vectorizer, key_words)
    # Find the corresponding articles
    for i in indexes:
        r = collection.find({'_id': i}, {"title": 1, "link": 1, "topic": 1, "authors": 1, "datetime": 1,
                                         "description": 1})
        for rr in r:
            results.append([rr['title'], rr['link'], rr['topic'], rr['authors'], rr['datetime'], rr['description']])
    return results
