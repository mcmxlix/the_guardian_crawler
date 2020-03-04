import re
import requests
from bs4 import BeautifulSoup


def scrape_page_title(soup):
    """ Function to extract the title of an article from the scrapped code """
    title = soup.find('h1', class_='content__headline').get_text()
    title = re.sub('\n', '', title)
    return title


def scrape_page_topic(soup):
    """ Function to extract the topic name of an article from the scrapped code """
    try:
        label = soup.find('span', class_='label__link-wrapper').get_text()
    except AttributeError:
        return "-"
    label = re.sub('\n', '', label)
    return label


def scrape_page_authors(soup):
    """ Function to extract the names of authors of an article from the scrapped code """
    authors = [re.sub('\n', '', a.get_text()) for a in soup.find_all('span', itemprop="name")]
    authors = ' & '.join([str(a) for a in authors])
    return authors


def scrape_page_datetime(soup):
    """ Function to extract the date of publication of an article from the scrapped code """
    datetime = [re.sub('\n', '', d.get_text()) for d in soup.find_all('time', itemprop="datePublished")]
    datetime = re.sub('\xa0', ' ', datetime[0])
    return datetime


def scrape_page_description(soup):
    """ Function to extract the description of the article from the scrapped code """
    try:
        descr = soup.find('div', class_="content__standfirst").get_text()
        descr = re.sub('\n', '', descr)
    except AttributeError:
        return "-"
    return descr


def scrape_page_text(soup):
    """ Function to extract the text of the article from the scrapped code """
    text = soup.find('div', class_="content__article-body")
    text = [t.get_text() for t in text.find_all('p')]
    text = ' '.join(t for t in text)
    return text


def scrape_page_related_topics(soup):
    """ Function to extract the links of the related topics of a given article from the scrapped code """
    links = [a['href'] for a in soup.find_all('a', class_='submeta__link')]
    return links


def scrape_page(link):
    """ Function returns the different information extracted from the page of an article"""
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = scrape_page_title(soup)
    link = link
    topic = scrape_page_topic(soup)
    related_topics_links = scrape_page_related_topics(soup)
    authors = scrape_page_authors(soup)
    datetime = scrape_page_datetime(soup)
    description = scrape_page_description(soup)
    text = scrape_page_text(soup)
    return title, link, topic, related_topics_links, authors, datetime, description, text


def home_page(link):
    """ Function returns the links to other articles from a given topic page """
    next_pages = []
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    for n in soup.find_all('a', class_='fc-item__link'):
        if n['href'] not in next_pages:
            next_pages.append(n['href'])
    return next_pages

