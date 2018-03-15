__author__ = 'Isaac Sung'

import requests
from bs4 import BeautifulSoup
from article_crawler import article_spider_multi_page

IMDB_BASE_URL = 'http://www.imdb.com'
IMDB_SEARCH_LINK = 'http://www.imdb.com/search/title?title_type=feature&release_date=1975-01-01,2017-12-31&user_rating=5.0,10.0&countries=us&sort=year,asc&page='
LINK_SEARCH_TERM = 'div.lister-item-image a'
start_page = 1
end_page = 2


def extract_duration(runtime):
    '''
    given a string in the format "1h 20min" extracts the running time in minutes
    '''
    runtime = runtime.split()
    hr = runtime[0]
    minutes = runtime[1]

    ind = hr.find("h")
    if ind != -1:
        hr = (int)(hr[:ind])
    else:
        print("h not found in runtime string.")

    ind = minutes.find("min")
    if ind != -1:
        minutes = (int)(minutes[:ind])
    else:
        print("min not found in runtime string.")

    return str((hr*60)+minutes)


def extract_info_from_page(link):
    '''
    Opens the link given in link and extracts information from that movie description page
    '''
    # open link and set up BeautifulSoup object
    source = requests.get(link)
    plain_text = source.text
    bs = BeautifulSoup(plain_text, 'html.parser')

    print(link)

    # extract Movie Title
    title = bs.select_one('div#ratingWidget p strong').string

    # extract Director Name
    director = bs.select_one('span[itemprop="director"] a span').string

    # extract content rating (G, PG, PG-13, etc)
    content_rating = bs.select_one('span[itemprop="contentRating"]')
    if content_rating is None:
        content_rating = "Not Rated"
    else:
        content_rating = content_rating.string

    # extract running time in minutes
    running_time = bs.select('time[itemprop="duration"]')
    if len(running_time) < 2:
        running_time = running_time[0].string
        running_time = extract_duration(running_time)
    else:
        running_time = bs.select('time[itemprop="duration"]')[1].string
        running_time = running_time.split()[0]
    print(running_time)

    # extract release year
    year = bs.select_one('')


def main():
    '''
    The main function that searches through the imdb website and crawls for movie pages and extracts information from them.
    '''
    links = article_spider_multi_page(IMDB_BASE_URL, IMDB_SEARCH_LINK, start_page, end_page, LINK_SEARCH_TERM)
    print(links)

    for link in links:
        extract_info_from_page(link)


if __name__ == '__main__':
    main()
