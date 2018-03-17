__author__ = 'Isaac Sung'

import requests
from bs4 import BeautifulSoup
from article_crawler import article_spider_multi_page

IMDB_BASE_URL = 'http://www.imdb.com'
IMDB_SEARCH_LINK = 'http://www.imdb.com/search/title?title_type=feature&release_date=1975-01-01,2017-12-31&user_rating=5.0,10.0&certificates=US%3Ag,US%3Apg,US%3Apg_13,US%3Ar&countries=us&sort=year,asc&page='
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

    # 1) extract Movie Title
    title = bs.select_one('div#ratingWidget p strong').string

    # 2) extract rating (out of 10)
    rating = bs.select_one('span[itemprop="ratingValue"]').string

    # 3) extract plot keywords
    keywords = bs.select('span[itemprop="keywords"]')
    keywords = [keyword.string for keyword in keywords]
    plot_keywords = ""
    for keyword in keywords:
        plot_keywords += keyword
        if keyword != keywords[-1]:
            plot_keywords += ";"

    # 4) extract content rating (G, PG, PG-13, etc)
    content_rating = bs.select_one('span[itemprop="contentRating"]')
    if content_rating is None:
        content_rating = "Not Rated"
    else:
        content_rating = content_rating.string

    # 5) extract running time in minutes
    running_time = bs.select('time[itemprop="duration"]')
    if len(running_time) < 2:
        running_time = running_time[0].string
        running_time = extract_duration(running_time)
    else:
        running_time = bs.select('time[itemprop="duration"]')[1].string
        running_time = running_time.split()[0]

    # 6) Extract genres
    genres = bs.select('a[href$="tt_stry_gnr"]')
    genres = [genre.string.strip() for genre in genres]

    # 7) Extract release date
    year = bs.select_one('div#ratingWidget p').get_text().split()[-1]
    year = year.translate({ord(c): None for c in '()'})

    # 13) Box office records
    budget = "n/a"
    opening_weekend = "n/a"
    gross_usa = "n/a"
    cumulative_gross = "n/a"
    txt_blocks = bs.select('div.txt-block')
    for block in txt_blocks:
        text = block.get_text()
        text = text.split()
        if "Budget:" in text[0]:
            budget = text[0][7:]
        elif "Opening" in text[0]:
            for string in text:
                if string[0] == "$":
                    opening_weekend = string[0:-1]
        elif "Gross" in text[0]:
            for string in text:
                if string[0] == "$":
                    gross_usa = string
                    if gross_usa[-1] == ',':
                        gross_usa = gross_usa[0:-1]
        elif "Cumulative" in text[0]:
            for string in text:
                if string[0] == "$":
                    cumulative_gross = string
                    if cumulative_gross[-1] == ",":
                        cumulative_gross = cumulative_gross[0:-1]
    print(cumulative_gross)



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
