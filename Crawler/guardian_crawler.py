import string
import pandas as pd
from Crawler.scrape_page_infos import home_page, scrape_page
from Crawler.mongodb_connection import insert_into_mongodb
from nltk.corpus import stopwords
import spacy

stop_words = stopwords.words('english')
nlp = spacy.load('en_core_web_sm')


def text_cleaning(text):
    """ Function to clean the scraped text """
    clean_text = []
    # List of special characters to remove
    xc = ['“', '”', '’', '-', '‘', '–', '…', "'", "'"]
    for x in xc:
        text = text.replace(x, ' ')
    text = text.replace('-', ' ')
    # Exclude stop words and lowercase text
    text = " ".join([w for w in text.split() if w not in stop_words]).lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Lemmatize text words
    text_words = " ".join([token.lemma_ for token in nlp(text) if token.lemma_ != '-PRON-'])
    clean_text.append(text_words)
    return clean_text[0]


def pages_parser(pages_to_scrape, crawler_df, scraped):
    """
    Function to extract title, authors, topic, datetime, description, text and related topics links for a given article
    """
    next_links = []
    # Check if there are pages to scrape
    if len(pages_to_scrape) != 0:
        for p in pages_to_scrape:
            # Verify if the address is not yet scrapped
            # In our case, we will limit the pages to be scraped to only 100
            if p not in scraped and len(scraped) < 100:
                try:
                    l = list(scrape_page(p))
                    l.append(text_cleaning(l[-1]))
                    # Insert the scraped information on a data frame
                    crawler_df.loc[len(crawler_df), :] = l
                    print(p)
                    # Update the list of scraped links
                    scraped.append(p)
                    # From a topic page in the 'related_topics_links', ..
                    # .. we will scrape the links of articles to be scrapped later
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
    """ Function to initialize variables to start crawling """
    # List of scraped links, it will be used to avoid duplicate scraping
    scraped = []
    # The first page from where we're going to start crawling
    pages_to_scrape = home_page("https://www.theguardian.com")
    cols = ["title", "link", "topic", "related_topics", "authors", "datetime", "description", "text", "clean_text"]
    # Data frame to store the scraped data, which will be sent to MongoDB Atlas later
    crawler_df = pd.DataFrame(columns=cols)
    return pages_parser(pages_to_scrape, crawler_df, scraped)


def lunch_crawler():
    """ Function to start crawling and save our data frame in MongoDB Atlas """
    print("*** START CRAWLING ***")
    theguardian_df = init_crawler()
    print("*** INSERT DATA INTO MONGODB ***")
    insert_into_mongodb(theguardian_df)
