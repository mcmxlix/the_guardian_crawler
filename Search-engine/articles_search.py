import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from Crawler.mongodb_connection import connect_to_mongodb


def train_tfidf(_df):
    clean_text = _df.clean_text
    vect = TfidfVectorizer()
    vect.fit(clean_text)
    tfidf = TfidfVectorizer().fit_transform(clean_text)
    return tfidf.toarray(), vect


def articles_parser(_df, tfidf, vect, key_words):
    _ids = []
    kw_tfidf = vect.transform([key_words])
    cosine_similarities = linear_kernel(kw_tfidf, tfidf).flatten()
    indexs = sorted(range(len(cosine_similarities)), key=lambda i: cosine_similarities[i], reverse=True)[-150:]
    for i in indexs:
        if cosine_similarities[i] > 0.1:
            _ids.append(_df._id[i])
    return _ids


def articles_search(kw):
    results = []
    collection = connect_to_mongodb()
    res = collection.find({}, {"_id": 1, "clean_text": 1})
    res_df = pd.DataFrame(columns=['_id', 'clean_text'])
    for x in res:
        res_df.loc[len(res_df), :] = [x['_id'], x['clean_text']]
    tfidf, vect = train_tfidf(res_df)
    _ids = articles_parser(res_df, tfidf, vect, kw)
    for i in _ids:
        r = collection.find({'_id': i}, {"title": 1, "link": 1, "topic": 1, "authors": 1, "datetime": 1,
                                         "descriptif": 1})
        for rr in r:
            results.append([rr['title'], rr['link'], rr['topic'], rr['authors'], rr['datetime'], rr['descriptif']])
    return results

