import requests
from bs4 import BeautifulSoup
import re

news = 'https://www.npr.org/sections/politics'
arts = 'https://www.npr.org/sections/world/'

topics = [news, arts]
index = 0
for topic in topics:
    source = requests.get(topic)
    plain_text = source.text
    bs = BeautifulSoup(plain_text, 'html.parser')
    links = bs.find_all('a', attrs = {'href':re.compile("^https://")}) 
    # Go through each link and only keep links to article that has 'storytext'
    filtered_links = []
    for link in links:
        link = link.get('href')
        if link not in filtered_links:
            filtered_links.append(link)
    # Go through each link and extract content if it is an article link
    article_link = []
    with open('indexNPR.txt', 'w') as index_file:
        for link in filtered_links:
            url = requests.get(link)
            html = url.text
            soup = BeautifulSoup(html, 'html.parser')
            article = soup.find(id = 'storytext')
            if article is not None:
                index_file.write(str(index) + ": " + link + '\n')
                article_link.append(link)
                print (str(index) + ": " + link )
                if article.aside is not None:
                    article.aside.extract()
                article_content = article.get_text()
                filename = str(index) + "_NPR.txt"
                with open(filename, 'w') as file:
                    file.write(article_content)
                index = index + 1
                


