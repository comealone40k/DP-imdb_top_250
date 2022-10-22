import pandas as pd
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

def all_page_link(start_url):
    all_urls = []
    url = start_url
    while(url != None):            #Loop around all the required webpages and terminates when last page arive!
        all_urls.append(url)
        soup = BeautifulSoup(requests.get(url).text,"html.parser")
        next_links = soup.find_all(class_='flat-button lister-page-next next-page')    #Extracts the next page link.
        if (len(next_links) == 0):         # If their is no next page, it returns 0.
            url = None
        else:
            next_page = "https://www.imdb.com" + next_links[0].get('href')
            url = next_page
    return all_urls

def scrape_imdb_top_250():
    main_array = []
    for url in tqdm(all_page_link("https://www.imdb.com/list/ls068082370/")):     #Runs the function for all the pages.
        soup = BeautifulSoup(requests.get(url).text,"html.parser")         #Extracts out the main html code.
        for link in soup.find_all(class_='lister-item-content'):
            id = int(link.find('span', {"class": "lister-item-index unbold text-primary"}).text[:-1])
            name = link.find('a').text
            rating = link.find('span',{"class":"ipl-rating-star__rating"}).text
            votes = int(link.find_all('span',{"name":"nv"})[0].text.replace(",",""))
            list_of_all = [id, name, rating, votes]
            main_array.append(list_of_all)
            soup_find = soup.find("script", type="application/ld+json")

            links_set = ()

    #this index variable contains the name of the columns of the data frame.
    index = ["id", "name", "rating", "votes"]

    df = pd.DataFrame(main_array,columns=index)   #creating the DataFrame using "main_array"

    return df