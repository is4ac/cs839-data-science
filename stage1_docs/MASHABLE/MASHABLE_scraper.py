import requests
from bs4 import BeautifulSoup

entertainment = 'https://mashable.com/entertainment/?utm_cid=mash-prod-nav-ch'
science = 'https://mashable.com/science/?utm_cid=mash-prod-nav-ch'

topics = [entertainment, science]
index = 0
for topic in topics:
    source = requests.get(topic)
    plain_text = source.text
    bs = BeautifulSoup(plain_text, 'html.parser')
    links = bs.find_all('article', class_='flat')
    # Go through each link and only keep links to article that has 'storytext'
    filtered_links = []
    for link in links:
        #print(link)
        link = link.a['href']
        #print (link)
        if 'https://mashable.com' not in links and link not in filtered_links:
            link = 'https://mashable.com' + link
            #print (link)
            filtered_links.append(link)
    # Go through each link and extract content if it is an article link
    article_link = []
    with open('indexMASHABLE.txt', 'w') as index_file:
        for link in filtered_links:
            url = requests.get(link)
            html = url.text
            soup = BeautifulSoup(html, 'html.parser')
            article = soup.find(class_ = 'article-content blueprint')
            if article is not None:
                if article.aside is not None:
                    article.aside.extract()
                article_content = article.get_text()    
                print (str(index) + ": " + link)
                index_file.write(str(index) + ": " + link + '\n')
                article_link.append(link)
                #print (str(index) + ": " + link )
                filename = str(index) + "_MASHABLE.txt"
                with open(filename, 'w') as file:
                    file.write(article_content)
                index = index + 1
                


