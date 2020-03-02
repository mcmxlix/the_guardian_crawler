import string
import pandas as pd
from theguardian_crawler.scrape_page_infos import home_page, scrape_page
from theguardian_crawler.mongodb_connection import insert_into_mongodb
from nltk.corpus import stopwords
import spacy

stop_words = stopwords.words('english')
nlp = spacy.load('en_core_web_sm')


def text_cleaning(text):
    clean_text = []
    xc = ['“', '”', '’', '-', '‘', '–', '…', "'", "'"]
    for x in xc:
        text = text.replace(x, ' ')
    text = text.replace('-', ' ')
    text = " ".join([w for w in text.split() if w not in stop_words]).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text_words = " ".join([token.lemma_ for token in nlp(text) if token.lemma_ != '-PRON-'])
    clean_text.append(text_words)
    return clean_text[0]


def pages_parser(pages_to_scrape, crawler_df, scraped):
    next_links = []
    if len(pages_to_scrape) != 0:
        for p in pages_to_scrape:
            if p not in scraped and len(scraped) < 100:
                try:
                    l = list(scrape_page(p))
                    l.append(text_cleaning(l[-1]))
                    crawler_df.loc[len(crawler_df), :] = l
                    print(p)
                    scraped.append(p)
                    for i in l[3]:
                        for y in home_page(i):
                            if y not in next_links and y not in scraped:
                                next_links.append(y)
                except AttributeError:
                    pass
        return pages_parser(next_links, crawler_df, scraped)
    else:
        return crawler_df


def init_crawler():
    scraped = []
    pages_to_scrape = home_page("https://www.theguardian.com")
    cols = ["title", "link", "topic", "related_topics", "authors", "datetime", "description", "text", "clean_text"]
    crawler_df = pd.DataFrame(columns=cols)
    return pages_parser(pages_to_scrape, crawler_df, scraped)


def lunch_crawler():
    print("*** START CRAWLING ***")
    theguardian_df = init_crawler()
    print("*** INSERT DATA INTO MONGODB ***")
    insert_into_mongodb(theguardian_df)

