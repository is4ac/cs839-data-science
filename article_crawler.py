__author__ = 'Isaac Sung'

import requests
from bs4 import BeautifulSoup

ATLANTIC_BASE = 'https://www.theatlantic.com'
ATLANTIC_FILMS = 'https://www.theatlantic.com/category/film/?page='
ATLANTIC_SELECT_TERM = 'li.article.blog-article a[data-omni-click="inherit"]'
VULTURE_BASE = ''
VULTURE = 'http://www.vulture.com/movies/'
VULTURE_SELECT_TERM = 'a.newsfeed-article-link'
WASHINGTONPOST_BASE = ''
WASHINGTONPOST = 'https://www.washingtonpost.com/goingoutguide/theater-dance'
WASHINGTONPOST_SELECT_TERM = 'a[data-pb-local-content-field="web_headline"]'
INDEX_FILE = 'stage1_docs/index.txt'
DIRECTORY = 'stage1_docs/raw/'


def article_spider_one_page(baseurl, searchurl, select_term):
    """
    Finds all the links to articles from a starting page.
    Will need to be tweaked for each specific web page.
    :param baseurl: the base name of the website (e.g. "https://www.theatlantic.com")
    :param searchurl: the starting place to search for articles (e.g. "https://www.theatlantic.com/category/film/")
    :return: a list of url's to articles
    """

    links = []

    # open link and set up BeautifulSoup object
    source = requests.get(searchurl)
    plain_text = source.text
    bs = BeautifulSoup(plain_text, 'html.parser')

    # Find all list elements with articles
    article_list = bs.select(select_term)
    for link in article_list:
        links.append(baseurl + link['href'])

    print('Links found on page ' + searchurl + ': ' + str(len(article_list)))

    return links


def article_spider_multi_page(baseurl, searchurl, max_pages, select_term):
    """
    Finds all the links to articles from a starting page.
    Will need to be tweaked for each specific web page.
    :param baseurl: the base name of the website (e.g. "https://www.theatlantic.com")
    :param searchurl: the starting place to search for articles (e.g. "https://www.theatlantic.com/category/film/")
    :param max_pages: the max number of pages to search (if applicable)
    :return: a list of url's to articles
    """

    links = []

    for page in range(1, max_pages+1):
        print('Currently on page ' + str(page) + '...')

        list = article_spider_one_page(baseurl, searchurl + str(page), select_term)
        links += list

        print('Links found on page ' + str(page) + ': ' + str(len(list)))

    return links

def text_extractor(url, filename):
    """
    Extracts the body of the article from a given URL and writes it to a text file.
    :param url: The url of the article to scrape
    :param filename: the name of the file to write to
    """

    #print("Extracting from link.. {}".format(url))

    # open link and set up BeautifulSoup object
    try:
        source = requests.get(url)
        plain_text = source.text
        bs = BeautifulSoup(plain_text, 'html.parser')

        # extract the article and remove extraneous info
        article_text = ''

        # Atlantic
        article = bs.find('section', id='article-section-1')
        if article is not None:
            if article.aside is not None:
                article.aside.extract()
            article_text = article.get_text()
        else:
            # Vulture
            article = bs.select_one('div.article-content')
            if article is not None:
                if article.div is not None:
                    article.div.extract()
                if article.aside is not None:
                    article.aside.extract()
                article_text = article.get_text()
            else:
                # Washington Post
                # there is a paywall.. I wonder if this will still work?
                article = bs.select_one('article[itemprop="articleBody"]')
                if article is not None:
                    if article.div is not None:
                        article.div.extract()
                article_text = article.get_text()

        # write text to file
        with open(filename, 'w') as file:
            file.write(article_text)
    except:
        print('Skipping unopenable link: ' + url)



def main():
    """
    Main code execution
    :return:
    """
    # dictionary to keep track of indices and http links
    link_ind = {}

    # new indices to add to file
    new_link_ind = {}

    # list of all links to articles
    links = []

    # determine start of index based on index.txt
    index = 0

    # index.txt stores the index number (filename of each text doc) and provides a link to the main article
    with open(INDEX_FILE, 'r') as file:
        for count, line in enumerate(file):
            # increment index as you read each line
            if len(line.strip()) > 0:
                link_ind[index] = line.split()[1]
                index = count+1

    # take all links from the following websites and extract them into .txt files
    links += article_spider_multi_page(ATLANTIC_BASE, ATLANTIC_FILMS, 2, ATLANTIC_SELECT_TERM)
    links += article_spider_one_page(VULTURE_BASE, VULTURE, VULTURE_SELECT_TERM)
    links += article_spider_one_page(WASHINGTONPOST_BASE, WASHINGTONPOST, WASHINGTONPOST_SELECT_TERM)

    for link in links:
        # check to see if the link has already been processed
        if link in iter(link_ind.values()):
            print("Link already exists in index. Skipping link {}.".format(link))
        else:
            # process link
            text_extractor(link, DIRECTORY + str(index) + '.txt')
            link_ind[index] = link
            new_link_ind[index] = link

        index += 1

    # write the link indices to a file so we can cross reference articles easily
    with open(INDEX_FILE, 'a') as file:
        for key in new_link_ind:
            file.write(str(key) + " " + new_link_ind[key] + "\n")

if __name__ == "__main__":
    main()
