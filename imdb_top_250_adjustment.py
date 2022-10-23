from datetime import datetime
import pandas as pd
import argparse
import scraper


def adjust_dataframe(p_df: pd.DataFrame, p_log_level: str = 'INFO'):
    # Get maximum amount of votes for all 250 movies
    l_max_votes = p_df.sort_values('rating', ascending=False).head(20).max(axis=0)['votes']

    # Adjust rating - 0.1 penalty for each 100k deviation from l_max_votes and create new column with adjusted value
    p_df['adjusted_rating1'] = p_df['rating'] + ((l_max_votes - p_df['votes']) // 100000 * -0.1)

    # Adjust rating - apply oscars adjustment and create new column
    p_df['adjusted_rating2'] = [scraper.oscars_adjustment(x) for x in p_df['oscars']]

    # Calculate final adjusted rating
    p_df['adjusted_rating'] = p_df['adjusted_rating1'] + p_df['adjusted_rating2']

    # Drop adjustment column - no need for them now
    l_df = p_df.drop("adjusted_rating1", axis='columns')
    l_df = l_df.drop("adjusted_rating2", axis='columns')

    # Sort movie list based on adjusted ratings, get top 20, reset index on DataFrame
    sorted_df = l_df.sort_values('adjusted_rating', ascending=False).head(20).reindex().reset_index(drop=True)

    # New index starts at 1
    sorted_df.index += 1

    return sorted_df


def extract_and_adjust(p_log_level: str = 'INFO'):

    # Get IMDB top 250 movie data
    df = scraper.extract_imdb_top_250_data(p_log_level=p_log_level)

    # Adjust rating and sort DataFrame
    sorted_df = adjust_dataframe(p_df=df, p_log_level=p_log_level)

    # Write adjusted movie data into CSV
    scraper.write_imdb_data_to_csv(p_df=sorted_df,
                                   p_file=f'imdb_top_250_adjusted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                   p_log_level=p_log_level)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", required=False, default='INFO',
                        help="Initiates log level, default='INFO'")
    input_args = parser.parse_args()
    extract_and_adjust(input_args.log_level)
