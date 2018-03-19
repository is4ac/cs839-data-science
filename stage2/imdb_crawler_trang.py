__author__ = 'Isaac Sung'

import requests
from bs4 import BeautifulSoup
from article_crawler import article_spider_multi_page
import pandas as pd
import os

IMDB_BASE_URL = 'http://www.imdb.com'
# IMDB_SEARCH_LINK = 'http://www.imdb.com/search/title?title_type=feature&release_date=1975-01-01,2017-12-31&user_rating=5.0,10.0&certificates=US%3Ag,US%3Apg,US%3Apg_13,US%3Ar&countries=us&sort=year,asc&page='
IMDB_SEARCH_LINK = 'http://www.imdb.com/search/title?title_type=feature&release_date=,2018-03-01&user_rating=7.5,&num_votes=100,&sort=moviemeter,asc'
LINK_SEARCH_TERM = 'div.lister-item-image a'
start_page = 1
end_page = 70


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

    return str((hr * 60) + minutes)


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
    keywords = list_to_string(keywords)

    # 4) extract content rating (G, PG, PG-13, etc)
    content_rating = bs.select_one('meta[itemprop="contentRating"]')
    if content_rating is None:
        content_rating = ""
    else:
        content_rating = content_rating['content']

    # 5) extract running time in minutes
    running_time = bs.select('time[itemprop="duration"]')
    if len(running_time) < 2:
        # print (running_time)
        if len(running_time) < 1:
            running_time = ""
        else:
            running_time = running_time[0].string
            running_time = extract_duration(running_time)
    else:
        running_time = bs.select('time[itemprop="duration"]')[1].string
        running_time = running_time.split()[0]

    # 6) Extract genres
    genres = bs.select('a[href$="tt_stry_gnr"]')
    genres = [genre.string.strip() for genre in genres]
    genres = list_to_string(genres)

    # 7) Extract release date
    year = bs.select_one('div#ratingWidget p').get_text().split()[-1]
    year = year.translate({ord(c): None for c in '()'})

    # 8) Extract director names
    directors_list = bs.select('div.credit_summary_item span[itemprop="director"] a span')
    directors = [director.text for director in directors_list]
    directors = list_to_string(directors)

    # 9) Extract writer names
    writers_list = bs.select('div.credit_summary_item span[itemprop="creator"] a span')
    writers = [writer.text for writer in writers_list]
    writers = list_to_string(writers)

    # 10) Extract actor names: only the top first 5 names
    actors_list = bs.select('td.itemprop a span.itemprop')
    actors = [actor.text for actor in actors_list]
    actors = actors[0:5]
    actors = list_to_string(actors)

    # 11-17)
    details = bs.select('div.txt-block')
    countries = []
    languages = []
    alternative_titles = []  # contains at most 1 alternative title
    production_companies = []
    budget = []
    opening_weekend = []
    gross_usa = []
    cumulative_gross = []
    for info in details:
        if info.h4 is None:
            continue
        else:
            # extract countries
            if info.h4.text == 'Country:':
                countries = [country.text for country in info.select('a[itemprop=\'url\']')]
            # extract languages
            if info.h4.text == 'Language:':
                languages = [language.text for language in info.select('a[itemprop=\'url\']')]
            # extract alternative titles
            if info.h4.text == 'Also Known As:':
                strings = [string for string in info.stripped_strings]
                alternative_titles.append(strings[1])  # assuming 'Also Known As' is the first string in the list
            # extract production companies
            if info.h4.text == 'Production Co:':
                production_companies = [company.text for company in info.select('span[itemprop="creator"] a span')]
            # extract budget
            if info.h4.text == 'Budget:':
                strings = [string for string in info.stripped_strings]
                budget.append(strings[1].replace(',', ''))
            if info.h4.text == 'Opening Weekend USA:':
                strings = [string for string in info.stripped_strings]
                opening_weekend.append(strings[1].replace(',', ''))
            if info.h4.text == 'Gross USA:':
                strings = [string for string in info.stripped_strings]
                gross_usa.append(strings[1].replace(',', ''))
            if info.h4.text == 'Cumulative Worldwide Gross:':
                strings = [string for string in info.stripped_strings]
                cumulative_gross.append(strings[1].replace(',', ''))

    countries = list_to_string(countries)
    languages = list_to_string(languages)
    alternative_titles = list_to_string(alternative_titles)
    production_companies = list_to_string(production_companies)
    budget = list_to_string(budget)
    opening_weekend = list_to_string(opening_weekend)
    gross_usa = list_to_string(gross_usa)
    cumulative_gross = list_to_string(cumulative_gross)

    return [title, actors, directors, writers, genres, keywords, \
            content_rating, running_time, year, languages, rating, \
            budget, cumulative_gross, opening_weekend, production_companies, \
            countries, alternative_titles]


def list_to_string(entity):
    # convert an entity list to string
    str = ''
    if type(entity) == list and len(entity) > 1:
        for i in range(0, len(entity) - 1):
            str = str + entity[i] + ';'
        str = str + entity[-1]
    elif type(entity) == list and len(entity) == 1:
        str = entity[0]
    elif type(entity) != list:
        str = entity
    return str


def main():
    '''
    The main function that searches through the imdb website and crawls for movie pages and extracts information from them.
    '''
    # CSV tables' columns
    headers = ['title', 'cast', 'directors', 'writers', 'genres', \
               'keywords', 'content_rating', 'run_time', 'release_year', \
               'languages', 'rating', 'budget', 'revenue', 'opening_weekend_revenue', \
               'production_companies', 'production_countries', 'alternative_titles']
    tuples = []
    # write links to a text file
    if not os.path.isfile('imdb_urls.txt'):
        links = article_spider_multi_page(IMDB_BASE_URL, IMDB_SEARCH_LINK, start_page, end_page, LINK_SEARCH_TERM)
        print("number of links: ", len(links))
        with open('imdb_urls.txt', 'w') as file:
            file.write('\n'.join(links))
    else:
        if not os.path.isfile('imdb_movies.csv'):
            with open('imdb_urls.txt', 'r') as f1:
                with open('imdb_processed_urls.txt', 'w') as f2:
                    with open('imdb_movies.csv', 'w') as f3:
                        df_headers = pd.DataFrame(columns=headers)
                        df_headers.to_csv(f3, encoding='latin-1', index=False)
                        for line in f1:
                            link = line.strip('\n')
                            tuple = extract_info_from_page(link)
                            tuple = pd.Series(tuple, index=headers)
                            df = df_headers.append(tuple, ignore_index=True)
                            df.to_csv(f3, mode='a', encoding='utf-8', index=False, header=False)
                            f2.write(link + '\n')
        else:
            existing_df = pd.read_csv('imdb_movies.csv', encoding='latin-1')
            # get row_count
            row_count = existing_df.shape[0]
            # open imdb_urls.txt file and start processing from (row_count)th link
            with open('imdb_urls.txt', 'r') as f1:
                lines = f1.readlines()[row_count:]
                # print (len(lines))
                # print (row_count)
            with open('imdb_processed_urls.txt', 'a') as f2:
                with open('imdb_movies.csv', 'a', encoding='utf-8') as f3:
                    df_headers = pd.DataFrame(columns=headers)
                    for line in lines:
                        link = line.strip('\n')
                        tuple = extract_info_from_page(link)
                        tuple = pd.Series(tuple, index=headers)
                        df = df_headers.append(tuple, ignore_index=True)
                        df.to_csv(f3, mode='a', encoding='utf-8', index=False, header=False)
                        f2.write(link + '\n')


##    for link in links:
##        tuple = extract_info_from_page(link)
##        tuples.append(tuple)
##    # create pandas dataframe
##    df = pd.DataFrame(tuples, columns = headers)
##    # write to csv
##    df.to_csv('IMDb_movies.csv', encoding = 'utf-8', index = False)


if __name__ == '__main__':
    main()