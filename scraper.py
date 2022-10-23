import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import html
from tqdm import tqdm
import re
import json
import logging
import config as c

logging.basicConfig(format=c.log_format)


def all_page_link(p_start_url: str, p_log_level: str = 'INFO') -> list:
    """
    Parses a given URL for hyperlinks and returns them in a list.
    Iterates through multiple pages if necessary.
    :param p_start_url: str
        Base URL to start searching on.
    :param p_log_level: str
        Log level to logging
    :return: list
        list of underlying hyperlinks
    """
    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    all_urls = []  # Container for acquired urls
    url = p_start_url  # Base of search

    logger.info(f'Start URL: {url}')

    while url is not None:  # Loop through the whole page until there is none
        all_urls.append(url)  # Add current url to container
        soup = BeautifulSoup(requests.get(url).text, "html.parser")  # Parse url content to find next page
        next_links = soup.find_all(class_='flat-button lister-page-next next-page')  # Extracts the next page link.
        if len(next_links) == 0:  # If there is no next page, it returns 0.
            url = None  # Ends the loop
            logger.debug('No more pages')

        else:
            next_page = "https://www.imdb.com" + next_links[0].get('href')  # Calculates next page link
            url = next_page
            logger.debug(f'Next page: {url}')

    logger.info('Finished')
    logger.debug(f'URLs:\n{all_urls}')

    return all_urls


def extract_imdb_data(p_content: str, p_log_level: str = 'INFO') -> list:
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

    soup = BeautifulSoup(p_content, 'html.parser')  # Parse page content

    soup_data = soup.find("script", type="application/ld+json").text  # Extract script data from page content

    logger.debug(f'Script data found:\n{soup_data}')

    imdb_data = json.loads(soup_data)  # Parse script data into JSON object

    # Movie names might contains html escape sequences
    # Must unescape them to get the actual name
    l_movie_name = html.unescape(imdb_data['name'])

    logger.debug(f'Data extracted from content:\n{imdb_data}')

    # Parse for data containing Awards won and Nominations info
    soup_oscars = soup.findAll("a",
                               attrs={"class": "ipc-metadata-list-item__label ipc-metadata-list-item__label--link"})

    num_of_oscars = 0  # Default Oscars won is zero
    for i in soup_oscars:  # If there is a section with relevant data, lopp through
        if re.search('Won(.+?)Oscars', i.text):  # If section contains text like 'Won X Oscars'
            num_of_oscars = int(re.findall(r'\d+', i.text)[0])  # Extract integer of Oscars won

            logger.debug(f'Found Oscars: {num_of_oscars} in: {i.text}')

    # There are some very rare cases, where date of release is not present
    # due to the movie being release before relevant info was recorded
    try:
        release_date = imdb_data['datePublished']  # Try getting datePublished field from movie data
    except KeyError as ke:  # in case there is no such field
        logger.warning(f'Publish date was not found for: {l_movie_name}')  # Log a warning and set release date as "N/A"
        release_date = 'N/A'

    l_return = [l_movie_name,
                release_date,
                imdb_data['aggregateRating']['ratingValue'],
                imdb_data['aggregateRating']['ratingCount'],
                num_of_oscars]

    logger.info(f'Finished, Extracted data: {l_return}')

    return l_return


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

    t = tqdm(all_page_link(p_start_url=l_top_250_url, p_log_level=p_log_level))  # Parse base url

    links_set = set()
    for i in t:
        soup = BeautifulSoup(requests.get(i).text, "html.parser")  # Parse current HTML page
        links = [a['href'] for a in soup.select('a[href]')]  # Find all links in parsed HTML page
        # Find movie links and deduplicate the resulting link set
        current_link_set = set(list(filter(lambda link: 'title/tt' in link, links)))

        logger.debug(f'Adding links:\n{current_link_set}')

        links_set = links_set.union(current_link_set)  # Add found links to link set

    logger.debug(f'Current set of links:\n{links_set}')

    imdb_top_250_data = []  # List to gather top 250 movie data into
    for link in links_set:
        l_current_link = f'https://www.imdb.com{link}'  # Calculate current movie link

        logger.debug(f'Extracting data from URL:{l_current_link}')

        l_content = str(requests.get(l_current_link).content)  # Extract content from movie url as string

        # Extract the IMDB data points
        imdb_top_250_data.append(extract_imdb_data(p_content=l_content, p_log_level=p_log_level))

    index = ["name", "release_date", "rating", "votes", "oscars"]  # Header for the DataFrame

    df = pd.DataFrame(imdb_top_250_data, columns=index)  # Turn extracted data into DataFrame

    logger.info(f'Finished, Result dataframe:\n{df}')

    return df


def oscars_adjustment(p_num_of_oscars: int) -> float:
    """
    Implements rating adjustment based on number of Academy Awards received.
    :param p_num_of_oscars: int
        Number of Oscars won by movie
    :return: float
        Adjustment value
    """

    if p_num_of_oscars == 0:
        return 0
    elif 0 < p_num_of_oscars < 3:
        return 0.3
    elif 2 < p_num_of_oscars < 6:
        return 0.5
    elif 5 < p_num_of_oscars < 11:
        return 1
    else:
        return 1.5


def write_imdb_data_to_csv(p_df: pd.DataFrame,
                           p_file: str,
                           p_sep: str = ';',
                           p_log_level: str = 'INFO'):
    """
    Writes IMDB data DataFrame to CSV file.
    Raises error when file already exists.
    :param p_df: pandas.DataFrame
        Source data for the file.
    :param p_file:
        Target file name / path.
    :param p_sep:
        Separator
    :param p_log_level: str
        Log level to logging
    :return: None
    """

    # Initiate logging for this function, pad it to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info(f'Started writing file: {p_file}')

    if os.path.isfile(p_file):  # Check if target file already exists.
        l_already_exists = f'File already exists: {p_file}'
        logger.error(l_already_exists)
        raise Exception(l_already_exists)  # Log error and raise exception - don't want to omit this error
    else:
        p_df.to_csv(path_or_buf=p_file, sep=p_sep, index=True, header=True, index_label='rank')

    logger.info(f'Finished writing file: {p_file}')
