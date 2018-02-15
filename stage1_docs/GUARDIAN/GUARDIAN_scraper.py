import requests
from bs4 import BeautifulSoup

love = 'https://www.theguardian.com/lifeandstyle/love-and-sex'
culture = 'https://www.theguardian.com/us/culture'

topics = [love, culture]
index = 0
for topic in topics:
    source = requests.get(topic)
    plain_text = source.text
    bs = BeautifulSoup(plain_text, 'html.parser')
    links = bs.find_all('div', class_ = 'fc-item__content') 
    # Go through each link and only keep links to article that has 'storytext'
    filtered_links = []
    for link in links:
        link = link.a['href']
        #print (link)
        if link not in filtered_links:
            filtered_links.append(link)
    # Go through each link and extract content if it is an article link
    article_link = []
    with open('indexGUARDIAN.txt', 'w') as index_file:
        for link in filtered_links:
            url = requests.get(link)
            html = url.text
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            article_content = ""
            if len(paragraphs) > 1:
                for paragraph in paragraphs:
                    article_content = article_content + paragraph.get_text()
            else:
                article_content = paragraphs.get_text()
            index_file.write(str(index) + ": " + link + '\n')
            article_link.append(link)
            print (str(index) + ": " + link )
            filename = str(index) + "_GUARDIAN.txt"
            with open(filename, 'w') as file:
                file.write(article_content)
            index = index + 1
                


