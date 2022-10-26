import csv
from datetime import datetime
import pandas as pd
import argparse
import imdb_scraper
import os
import logging
import config as c

logging.basicConfig(format=c.log_format)


def oscars_adjustment(p_num_of_oscars: int) -> float:
    """
    Implements rating adjustment based on number of Academy Awards received.
    :param p_num_of_oscars: int
        Number of Oscars won by movie
    :return: float
        Adjustment value
    """
    if p_num_of_oscars < 0:
        raise Exception(f'The number of Oscars parameter is below zero ("{p_num_of_oscars}"). No movie is THAT bad.')

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


def adjust_dataframe(p_df: pd.DataFrame, p_log_level: str = 'INFO'):

    # Initiate logging for this function, pad function name to 30 characters
    logger = logging.getLogger(__name__.ljust(30, ' '))
    logger.setLevel(p_log_level)

    logger.info('Started')

    # Get maximum amount of votes for all 250 movies
    l_max_votes = p_df.sort_values('rating', ascending=False).head(20).max(axis=0)['votes']

    logger.info(f'Maximum number of votes in the set: {l_max_votes}')

    # Adjust rating - 0.1 penalty for each 100k deviation from l_max_votes and create new column with adjusted value
    p_df['review_penalty'] = ((l_max_votes - p_df['votes']) // 100000 * -0.1)

    logger.info('Vote/Review penalties are calculated')

    # Adjust rating - apply oscars adjustment and create new column
    p_df['oscars_adjustment'] = [oscars_adjustment(x) for x in p_df['oscars']]

    logger.info('Oscars adjustments are calculated')

    # Calculate final adjusted rating
    p_df['adjusted_rating'] = round(p_df['rating'] + p_df['review_penalty'] + p_df['oscars_adjustment'], 1)

    logger.info('Final adjustments are calculated')

    # Drop adjustment column - no need for them now
    l_df = p_df.drop("oscars_adjustment", axis='columns')
    l_df = l_df.drop("review_penalty", axis='columns')

    # Sort movie list based on adjusted ratings, get top 20, reset index on DataFrame
    sorted_df = l_df.sort_values('adjusted_rating', ascending=False).reindex().reset_index(drop=True)

    # New index starts at 1
    sorted_df.index += 1

    sorted_df.insert(loc=0, column='rank', value=sorted_df.index)

    sorted_df['rank'] = sorted_df.index

    logger.info('DataFrame adjustment is done.')

    return sorted_df


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
        p_df.to_csv(path_or_buf=p_file, sep=p_sep, index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)

    logger.info(f'Finished writing file: {p_file}')


def extract_and_adjust(p_log_level: str = 'INFO'):

    # Get IMDB top 250 movie data
    df = imdb_scraper.extract_imdb_top_250_data(p_log_level=p_log_level)

    # Adjust rating and sort DataFrame, round ratings to 1 decimal
    sorted_df = adjust_dataframe(p_df=df, p_log_level=p_log_level).round(1)

    # Write adjusted movie data into CSV
    write_imdb_data_to_csv(p_df=sorted_df,
                           p_file=f'imdb_top_250_adjusted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                           p_log_level=p_log_level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", required=False, default='INFO',
                        help="Initiates log level, default='INFO'")
    input_args = parser.parse_args()
    extract_and_adjust(input_args.log_level)
