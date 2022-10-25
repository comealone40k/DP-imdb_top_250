import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import html
import re
import json
import logging
import config as c

logging.basicConfig(format=c.log_format)


def extract_number_of_oscars(p_soup: BeautifulSoup, p_log_level: str = 'INFO') -> int:
    """
    Extract number of Oscars won by movie by parsing the movie page content, looking
    for the metadata list items and using regex to narrow the list.
    :param p_soup: BeautifulSoup
        soup to extract Oscars data from.
    :param p_log_level: str
        Log level to logging
    :return: int
        Number of Oscars won by movie
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    # Parse for data containing Awards won and Nominations info
    soup_oscars = p_soup.findAll("a",
                                 attrs={"class": "ipc-metadata-list-item__label ipc-metadata-list-item__label--link"})

    num_of_oscars = 0  # Default Oscars won is zero
    for i in soup_oscars:  # If there is a section with relevant data, lopp through
        if re.search('Won(.+?)Oscars', i.text):  # If section contains text like 'Won X Oscars'
            num_of_oscars = int(re.findall(r'\d+', i.text)[0])  # Extract integer of Oscars won

            logger.debug(f'Found Oscars: {num_of_oscars} in: {i.text}')

    return num_of_oscars


def extract_number_of_reviews(p_content: bytes, p_log_level: str = 'INFO') -> int:
    """
    Extracts data from IMDB page content: "num_of_reviews"
    :param p_content: str
        Content of the page to extract from ( Html response )
    :param p_log_level: str
        Log level to logging
    :return: int
        Number of reviews for movie
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    logger.debug(f'Current content:\n{p_content}')

    l_review_soup = BeautifulSoup(p_content, 'html.parser')

    l_reviews_text = l_review_soup.find("div", attrs={"class": "lister"}).find('div').find('div').find('span').text

    logger.debug(f'Review data found:\n{l_reviews_text}')

    l_num_of_reviews = int(re.findall(r'\d+', l_reviews_text.replace(',', ''))[0])

    return l_num_of_reviews


def extract_imdb_json_from_content(p_soup: BeautifulSoup, p_log_level: str = 'INFO') -> dict:
    """
    Extract JSON data from JavaScript application data, parses it into a dictionary.
    :param p_soup: BeautifulSoup
        Parsed page content of the movie.
    :param p_log_level: str
        Log level to logging.
    :return: dict
        Parsed JSON data from JavaScript application data.
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    l_soup_data = p_soup.find("script", type="application/ld+json").text  # Extract script data from page content

    logger.debug(f'Script data found:\n{l_soup_data}')

    l_imdb_data = json.loads(l_soup_data)  # Parse script data into JSON object

    logger.debug(f'Data extracted from content:\n{l_imdb_data}')

    return l_imdb_data


def extract_imdb_data_from_json(p_json: dict, p_log_level: str = 'INFO') -> list:
    """
    Extracts the necessary fields from the parsed JSON application data from movie page.
    Returns them in a list ["name", "release_date", "rating", "votes", "oscars"]
    :param p_json:
        Parsed JSON data from JavaScript application data.
    :param p_log_level: str
        Log level to logging
    :return: list
        List of necessary fields for further calculation
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    # Movie names might contains html escape sequences
    # Must unescape them to get the actual name
    l_movie_name = html.unescape(p_json['name'])

    # There are some very rare cases, where date of release is not present
    # due to the movie being release before relevant info was recorded
    try:
        release_date = p_json['datePublished']  # Try getting datePublished field from movie data
    except KeyError as ke:  # in case there is no such field
        logger.warning(f'Publish date was not found for: {l_movie_name}')  # Log a warning and set release date as "N/A"
        release_date = 'N/A'

    l_return = [l_movie_name,
                release_date,
                p_json['aggregateRating']['ratingValue'],
                p_json['aggregateRating']['ratingCount']]

    logger.info(f'Finished, Extracted data: {l_return}')

    return l_return


def extract_imdb_data(p_content: bytes, p_log_level: str = 'INFO') -> list:
    """
    Extracts data from IMDB page content: "name", "release_date", "rating", "votes", "oscars"
    :param p_content: str
        Content of the page to extract from ( Html response )
    :param p_log_level: str
        Log level to logging
    :return: list
        List of extracted content: "name", "release_date", "rating", "votes", "oscars"
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    logger.debug(f'Current content:\n{p_content}')

    l_soup = BeautifulSoup(p_content, 'html.parser')  # Parse page content

    # Extract json data from movie page content
    l_imdb_json = extract_imdb_json_from_content(p_soup=l_soup, p_log_level=p_log_level)

    # Extract number of Oscars won by movie
    l_num_of_oscars = extract_number_of_oscars(p_soup=l_soup, p_log_level=p_log_level)

    # Extract necessary data points from json data
    l_imdb_data = extract_imdb_data_from_json(p_json=l_imdb_json, p_log_level=p_log_level)

    # Append number of Oscars won to extracted json data
    l_imdb_data.append(l_num_of_oscars)

    logger.info(f'Finished, Extracted data: {l_imdb_data}')

    return l_imdb_data


def extract_imdb_top_250_data(p_log_level: str = 'INFO') -> pd.DataFrame:
    """
    Extracts movie URLs from the IMDB top 250 page and mines relevant info from their content
    Returns the data in pandas DataFrame
    :param p_log_level: str
        Log level to logging
    :return: pandas.DataFrame
        Extracted data
    """

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    l_top_250_url = c.top_250_url  # Get url from config to avoid code changes if url changes if ever

    logger.debug(f'Starting on URL: {l_top_250_url}')

    soup = BeautifulSoup(requests.get(l_top_250_url).text, "html.parser")  # Parse top 250 url

    l_title_list_soup = soup.find('script', type="application/ld+json").text  # Find movie link list in script tag

    l_title_json = json.loads(l_title_list_soup)  # Parse link list into JSON object

    l_title_list = l_title_json['about']['itemListElement']  # Get links from JSON

    filtered = list(filter(lambda pos: int(pos['position']) <= 20, l_title_list))  # Filter on position ( 20 or less )

    link_list = [x['url'] for x in filtered]  # Extract url from link list

    imdb_top_250_data = []  # List to gather top 250 movie data into

    # Looping though movie links
    for link in link_list:
        l_current_link = f'https://www.imdb.com{link}'  # Calculate current movie link

        logger.debug(f'Extracting data from URL:{l_current_link}')

        l_content = requests.get(l_current_link).content  # Extract content from movie url as bytes

        logger.debug(f'Extracting bytes content from URL:{l_content}')

        # Extract the IMDB data points
        imdb_top_250_data.append(extract_imdb_data(p_content=l_content, p_log_level=p_log_level))

    index = ["name", "release_date", "rating", "votes", "oscars"]  # Header for the DataFrame

    df = pd.DataFrame(imdb_top_250_data, columns=index)  # Turn extracted data into DataFrame

    logger.info(f'Finished, Result dataframe:\n{df}')

    return df
