import scraper
import imdb_top_250_adjustment
import unittest
import pandas as pd
from bs4 import BeautifulSoup
import json
from Tests import test_data
import os


class TestIMDBScraper(unittest.TestCase):

    def test_json_parser(self):

        for movie_json in test_data.test_data['movie_jsons']:

            l_json = json.loads(movie_json['movie_json'])
            l_test_results = movie_json['expected_result_list']

            print(f'Movie JSON: {l_json}')
            print(f'Expected results: {l_test_results}')

            l_parse_result = scraper.extract_imdb_data_from_json(p_json=l_json, p_log_level='DEBUG')

            print(f'Parse results: {l_parse_result}')

            assert l_test_results == l_parse_result, 'Parse result and expected results do not match'

    def test_content_scraper(self):

        for movie_data in test_data.test_data['movie_byte_files']:

            file_name = movie_data['file_name']

            with open(file_name, "rb") as binary_file:
                l_bdata = binary_file.read()

            l_test_num_of_oscars = movie_data['oscars']

            print(f'File name: {file_name} Oscars test number:{l_test_num_of_oscars}')

            l_soup = BeautifulSoup(l_bdata, 'html.parser')

            number_of_oscars = scraper.extract_number_of_oscars(p_soup=l_soup)

            print(f'File name: {file_name} Oscars extracted number:{number_of_oscars}')

            assert number_of_oscars == l_test_num_of_oscars, \
                f'Number of Oscars won is not matching test data, file name: {file_name}'

            l_test_data = [movie_data['title'],
                           movie_data['date_published'],
                           movie_data['rating'],
                           movie_data['votes']]

            print(f'File name: {file_name} Test data:{l_test_data}')

            l_json = scraper.extract_imdb_json_from_content(p_soup=l_soup)

            l_extracted_fields = scraper.extract_imdb_data_from_json(p_json=l_json)

            print(f'File name: {file_name} Extracted fields:{l_extracted_fields}')

            assert l_extracted_fields == [movie_data['title'],
                                          movie_data['date_published'],
                                          movie_data['rating'],
                                          movie_data['votes']], \
                f'Data extracted from JSON is not mathcing test data, file name: {file_name}'

    def test_oscars_adjustments(self):

        for oscars in test_data.test_data['oscars_adjustments']:

            l_num_of_oscars = oscars['oscars']
            l_expected_adjustment = oscars['adjustment']
            l_oscars_adjustment = imdb_top_250_adjustment.oscars_adjustment(p_num_of_oscars=l_num_of_oscars)

            print(f'Number of Oscars: {l_num_of_oscars}, '
                  f'Expected adjustment: {l_expected_adjustment}, '
                  f'Result: {l_oscars_adjustment}')

            assert l_expected_adjustment == l_oscars_adjustment, 'Calculated adjustment does not match expected results'

    def test_dataframe_adjustments(self):

        l_source_index = ["name", "release_date", "rating", "votes", "oscars"]

        l_expected_index = ["name", "release_date", "rating", "votes", "oscars", "adjusted_rating"]

        l_expected_df = pd.DataFrame(test_data.test_data['dataframe_adjustments_results'], columns=l_expected_index)

        l_expected_df.index += 1

        print(f'Expected dataframe:\n{l_expected_df}')

        l_df = pd.DataFrame(test_data.test_data['dataframe_adjustments'], columns=l_source_index)

        l_result_df = imdb_top_250_adjustment.adjust_dataframe(p_df=l_df)

        print(f'Result dataframe:\n{l_result_df}')

        pd.testing.assert_frame_equal(l_expected_df, l_result_df)

    def test_csv_writer(self):

        l_file_name = 'imdb_top_250_adjusted_test.csv'
        if os.path.exists(l_file_name):
            os.remove(l_file_name)

        l_expected_index = ["name", "release_date", "rating", "votes", "oscars", "adjusted_rating"]

        l_expected_df = pd.DataFrame(test_data.test_data['dataframe_to_csv'], columns=l_expected_index)

        imdb_top_250_adjustment.write_imdb_data_to_csv(p_df=l_expected_df,
                                                       p_file=l_file_name)

        l_read_df = pd.read_csv(l_file_name, sep=';', na_filter=False, keep_default_na=False)

        print(f'Original DataFrame:\n{l_expected_df}')

        print(f'Read DataFrame:\n{l_read_df}')

        pd.testing.assert_frame_equal(l_expected_df, l_read_df)

        os.remove(l_file_name)

if __name__ == '__main__':
    unittest.main()
