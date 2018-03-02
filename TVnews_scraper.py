import requests
from bs4 import BeautifulSoup
import os

# news urls
love = 'https://www.theguardian.com/lifeandstyle/love-and-sex'
culture = 'https://www.theguardian.com/us/culture'
sports = 'https://www.theguardian.com/us/sport' 
entertainment = 'https://mashable.com/entertainment/?utm_cid=mash-prod-nav-ch'
science = 'https://mashable.com/science/?utm_cid=mash-prod-nav-ch'

# topics
Guardian_topics = [love, culture, sports]
Mashable_topics = [entertainment, science]

# directory and file paths
INDEX_FILE = 'stage1_docs/Data/index.txt'
DATA_FOLDER = 'stage1_docs/Data/raw/'

def main():
    # scrape news from the Guardian
    Guardian_links = Guardian_scraper(Guardian_topics)
    # scrape news from Mashable
    Mashable_links = Mashable_scraper(Mashable_topics)
    index = 0
    with open(INDEX_FILE, 'w') as index_file:
        # extract text from the Guardian
        index = text_extractor(Guardian_links, 'Guardian', index, index_file)
        # extract text from Mashable
        index = text_extractor(Mashable_links, 'Mashable', index, index_file)
    
def Guardian_scraper(Guardian_topics):
    filtered_links = []
    for topic in Guardian_topics:
        source = requests.get(topic)
        plain_text = source.text
        bs = BeautifulSoup(plain_text, 'html.parser')
        links = bs.find_all('div', class_ = 'fc-item__content') 
        for link in links:
            link = link.a['href']
            if 'www.theguardian.com' in link and link not in filtered_links:
                filtered_links.append(link)
    return filtered_links

def Mashable_scraper(Mashable_topics):
    filtered_links = []
    for topic in Mashable_topics:
        source = requests.get(topic)
        plain_text = source.text
        bs = BeautifulSoup(plain_text, 'html.parser')
        links = bs.find_all('article', class_='flat')
        for link in links:
            link = link.a['href']
            if 'https://mashable.com' not in links and link not in filtered_links:
                link = 'https://mashable.com' + link
                filtered_links.append(link)
    return filtered_links

def text_extractor(links, page_name, index, index_file):
    for link in links:
        #print (link)
        url = requests.get(link)
        html = url.text
        soup = BeautifulSoup(html, 'html.parser')
        article_content = ''
        # Extract text from the Guardian
        if page_name == 'Guardian':
            paragraphs = soup.find_all('p')
            article_content = ""
            if len(paragraphs) > 1:
                for paragraph in paragraphs:
                    article_content = article_content + paragraph.get_text()
            else:
                article_content = paragraphs.get_text()
        # Extract text from Mashable
        elif page_name == 'Mashable':
            article = soup.find(class_ = 'article-content blueprint')
            if article is not None:
                if article.aside is not None:
                    article.aside.extract()
                article_content = article.get_text()    
        # Write article_content to txt file, add link to index_file         
        if len(article_content) > 0:
            index_file.write(str(index) + ": " + link + '\n')
            filename = DATA_FOLDER + str(index) + "_" + page_name + ".txt"
            with open(filename, 'w', encoding  = 'utf-8') as file:
                file.write(article_content)
            index = index + 1
    return index
                
if __name__ == "__main__":
    main()

