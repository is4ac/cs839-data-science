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
    
    # extract countries, languages, alternative titles, production companies:
    details = bs.select('div.txt-block')
    countries = []
    languages = []
    alternative_titles = [] # contains at most 1 alternative title
    production_companies = []
    for info in details:
        # extract countries
        if info.h4 is None:
            continue
        else:
            if info.h4.text == 'Country:':
                countries = [country.text for country in info.select('a[itemprop=\'url\']')]
            # extract languages
            if info.h4.text == 'Language:':
                languages = [language.text for language in info.select('a[itemprop=\'url\']')]
            # extract alternative titles
            if info.h4.text == 'Also Known As:':
                strings = [string for string in info.stripped_strings]
                alternative_titles.append(strings[1]) # assuming 'Also Known As' is the first string in the list
            # extract production companies
            if info.h4.text == 'Production Co:':
                production_companies = [company.text for company in info.select('span[itemprop="creator"] a span')]
            
    # extract director names
    directors_list = bs.select('div.credit_summary_item span[itemprop="director"] a span')
    directors = [director.text for director in directors_list]
        
    # extract writer names
    writers_list = bs.select('div.credit_summary_item span[itemprop="creator"] a span')
    writers = [writer.text for writer in writers_list]
    
    # extract actor names: only the top first 5 names
    actors_list = bs.select('td.itemprop a span.itemprop')
    actors = [actor.text for actor in actors_list]
    actors = actors[0:5]

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
    #print(cumulative_gross)
    
    return title, rating, plot_keywords, content_rating, running_time, genres, year, directors, writers, actors, \
           countries, languages, alternative_titles, production_companies

    
def main():
    '''
    The main function that searches through the imdb website and crawls for movie pages and extracts information from them.
    '''
    links = article_spider_multi_page(IMDB_BASE_URL, IMDB_SEARCH_LINK, start_page, end_page, LINK_SEARCH_TERM)
    print("number of links: ", len(links))
    for link in links:
        A, B, C, D, E, F, G, H, I, J, K, L, M, N = extract_info_from_page(link)
        print (A)
        print (B)
        print (C)
        print (D)
        print (E)
        print (F)
        print (G)
        print(H)
        print(I)
        print(J)
        print(K)
        print(L)
        print(M)
        print(N)


if __name__ == '__main__':
    main()
