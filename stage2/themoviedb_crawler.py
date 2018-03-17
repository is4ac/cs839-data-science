__author__ = 'Hoai Nguyen'

import csv
import requests
import os
from bs4 import BeautifulSoup

TITLE = 'Title'
USER_SCORE = 'User Score'
DIRECTOR = 'Director'
SCREENPLAY = 'Screenplay'
TOP_BILLED_CAST = 'Top Billed Cast'
RELEASE_DATE = 'Release Date'
CONTENT_RATING = 'Content Rating'
GENRES = 'Genres'
KEYWORDS = 'Keywords'
REVENUE = 'Revenue'
LANGUAGE = 'Original Language'
RUNTIME = 'Runtime'
BUDGET = 'Budget'
HOMEPAGE = 'Homepage'

ATTRIBUTES = [TITLE, USER_SCORE, DIRECTOR, SCREENPLAY, TOP_BILLED_CAST, RELEASE_DATE, 
              CONTENT_RATING, GENRES, KEYWORDS, REVENUE, LANGUAGE, RUNTIME, BUDGET,
              HOMEPAGE]
              
def get_entity(url):
    """For each url, returns an entity with attributes in ATTRIBUTES."""
    source = requests.get(url, allow_redirects = True)
    plain_text = source.text 
    soup = BeautifulSoup(plain_text, 'html.parser')
    entity = {} 
    for att in ATTRIBUTES:
        entity[att] = ''

    # Extract title.
    title = soup.find("meta", property="og:title")
    entity[TITLE] = title.get("content")

    # Extract User Score.
    score = soup.find("div", class_="user_score_chart")
    entity[USER_SCORE] = score.get("data-percent")

    # Extract Crew
    crews = soup.find_all("li", class_="profile")
    directors = []
    screenplays = []
    for entry in crews:
        p = entry.find_all("p")
        if len(p) == 2:
            for crew in p[1].get_text().split(','):
                if crew.strip() == DIRECTOR:
                    directors.append(p[0].get_text())
                if crew.strip() == SCREENPLAY:
                    screenplays.append(p[0].get_text())
    entity[DIRECTOR] = ",".join(directors)
    entity[SCREENPLAY] = ",".join(screenplays)
    
    # Top billed cast
    topcastnames = []
    castnames = soup.find_all("li", class_="card")
    for card in castnames:
        p = card.find_all("p")
        # print(p[0].get_text())
        topcastnames.append(p[0].get_text())
    entity[TOP_BILLED_CAST] = ",".join(topcastnames)
    

    # Extract attribute from fact section.
    facts_section = soup.find("section", class_="facts left_column")
    for line in facts_section.get_text().split('\n'):
        for att in ATTRIBUTES:
            if line.startswith(att):
                value = line.replace(att, '').strip()
                entity[att] = value

    # Extract attribute from genres section.
    genres_section = soup.find("section", class_="genres right_column")
    genres = []
    for line in genres_section.find_all("li"):
        genres.append(line.get_text())

    entity[GENRES] = ",".join(genres)

    # Extract Release Date.
    release_date = soup.find("div", class_="header_poster_wrapper")
    date = release_date.find("span", class_="release_date")
    entity[RELEASE_DATE] = date.get_text().replace('(', '').replace(')', '')

    # Extract Content Rating.
    content = soup.find("div", class_="content_score")
    entity[CONTENT_RATING] = content.get_text().strip()

    # Extract Keywords
    keywords_section = soup.find("section", class_="keywords right_column")
    keywords = []
    for line in keywords_section.find_all("li"):
        keywords.append(line.get_text())
       
    entity[KEYWORDS] = ",".join(keywords)

    # Construct data to be written to CSV.
    row = []
    for att in ATTRIBUTES:
        row.append(entity[att])
    return row

def get_all_urls():
    """Returns all links to crawl. This function will crawl everything
    from the website. So could be slow. 

    Used only to generate the urls once.
    """
    # We first read from 'Data/themoviedb_crawl_urls
    urls = []
    START_PAGE = 'https://www.themoviedb.org/movie/top-rated?page=%s'
    for i in range(1, 276):
        page_url = START_PAGE % str(i)
        print ('Crawl for movie links on page: ' + page_url)
        source = requests.get(page_url, allow_redirects = True)
        plain_text = source.text
        soup = BeautifulSoup(plain_text, 'html.parser')
        for a in soup.find_all("a", class_="title result"):
            movie_url = 'https://www.themoviedb.org' + a.get('href')
            urls.append(movie_url)
    return urls

CRAWLED_URLS = 'Data/themoviedb_crawled_urls.txt'

def get_urls():
    """Returns a list of url to crawl. Skip the one already been crawled."""
    ALL_URLS = 'Data/themoviedb_all_urls.txt'
    if os.path.exists(ALL_URLS) or os.path.isfile(ALL_URLS):
        print('Skip creating ' + ALL_URLS)
    else:
        print('Creating ' + ALL_URLS)
        with open(ALL_URLS, 'w') as text_file:
            for url in get_all_urls():
                text_file.write(url + '\n')
    # Now, have a set of all urls we have to crawl.
    all_urls = set()
    with open(ALL_URLS) as f:
        all_urls.update(f.readlines())
    # Next, build a set of crawed urls by reading from ALL_URLS.
    # This set is used to skip the urls that we have crawled.
    crawled_urls = set()
    # Next, for each url in ALL_URLS, check if it has been crawled
    # A crawled url must exist in CRAWLED_URLS file.
    if os.path.exists(CRAWLED_URLS):
        with open(CRAWLED_URLS) as f:
            crawled_urls.update(f.readlines())
    return all_urls - crawled_urls

def main():
    """Main entry point of the program."""
    CSV_FILE = 'Data/themoviedb.csv'
    create_file_for_the_first_time = not os.path.exists(CSV_FILE)
    csvfile = open(CSV_FILE, 'a')
    writer = csv.writer(csvfile, delimiter='|')
    if (create_file_for_the_first_time):
        writer.writerow(ATTRIBUTES)
    with open(CRAWLED_URLS, 'a') as crawled_url_file:
        urls = get_urls()
        print('Total url needs to crawl: ' + str(len(urls)))
        for url in urls:
            print('Crawling ' + url)
            writer.writerow(get_entity(url))
            crawled_url_file.write(url)
    csvfile.close()

if __name__ == "__main__":
    main()
