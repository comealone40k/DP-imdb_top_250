test_data = {
    "movie_jsons": [{"movie_json": """{"name": "Revenge of the Cactus 1", "aggregateRating": {"@type": "AggregateRating", "ratingCount": 100000, "bestRating": 10, "worstRating": 1, "ratingValue": 9}}""", "expected_result_list": ["Revenge of the Cactus 1", "N/A", 9, 100000]},
                    {"movie_json": """{"name": "Revenge of the Cactus 2", "aggregateRating": {"@type": "AggregateRating", "ratingCount": 150000, "bestRating": 10, "worstRating": 1, "ratingValue": 8.5}, "datePublished": "2001-01-01"}""", "expected_result_list": ["Revenge of the Cactus 2", "2001-01-01", 8.5, 150000]},
                    {"movie_json": """{"name": "Revenge of the Cactus 3", "aggregateRating": {"@type": "AggregateRating", "ratingCount": 200000, "bestRating": 10, "worstRating": 1, "ratingValue": 7.2}, "datePublished": "2003-04-24"}""", "expected_result_list": ["Revenge of the Cactus 3", "2003-04-24", 7.2, 200000]},
                    {"movie_json": """{"name": "Revenge of the Cactus 4", "aggregateRating": {"@type": "AggregateRating", "ratingCount": 250000, "bestRating": 10, "worstRating": 1, "ratingValue": 5.7}, "datePublished": "2007-10-13"}""", "expected_result_list": ["Revenge of the Cactus 4", "2007-10-13", 5.7, 250000]},
                    {"movie_json": """{"name": "Revenge of the Cactus 5", "aggregateRating": {"@type": "AggregateRating", "ratingCount": 95613, "bestRating": 10, "worstRating": 1, "ratingValue": 3.2}, "datePublished": "2015-12-24"}""", "expected_result_list": ["Revenge of the Cactus 5", "2015-12-24", 3.2, 95613]}
                    ],

    'movie_byte_files': [{'file_name': 'Tests/title_tt001.txt', 'title': 'The Kid', 'date_published': '1924-08-22', 'rating': 8.3, 'votes': 126562, 'oscars': 0},
                         {'file_name': 'Tests/title_tt002.txt', 'title': 'The Gold Rush', 'date_published': '1926-03-04', 'rating': 8.2, 'votes': 111544, 'oscars': 0},
                         {'file_name': 'Tests/title_tt003.txt', 'title': 'Metropolis', 'date_published': '1927-02-17', 'rating': 8.3, 'votes': 174351, 'oscars': 0},
                         {'file_name': 'Tests/title_tt004.txt', 'title': 'The General', 'date_published': 'N/A', 'rating': 8.2, 'votes': 91609, 'oscars': 0},
                         {'file_name': 'Tests/title_tt005.txt', 'title': 'The Lord of the Rings: The Return of the King', 'date_published': '2004-01-08', 'rating': 9, 'votes': 1829070, 'oscars': 11}
                         ],

    'oscars_adjustments': [{'oscars': 0, 'adjustment': 0},
                           {'oscars': 1, 'adjustment': 0.3},
                           {'oscars': 2, 'adjustment': 0.3},
                           {'oscars': 3, 'adjustment': 0.5},
                           {'oscars': 4, 'adjustment': 0.5},
                           {'oscars': 5, 'adjustment': 0.5},
                           {'oscars': 6, 'adjustment': 1},
                           {'oscars': 7, 'adjustment': 1},
                           {'oscars': 8, 'adjustment': 1},
                           {'oscars': 9, 'adjustment': 1},
                           {'oscars': 10, 'adjustment': 1},
                           {'oscars': 11, 'adjustment': 1.5},
                           {'oscars': 12, 'adjustment': 1.5},
                           {'oscars': 13, 'adjustment': 1.5},
                           {'oscars': 14, 'adjustment': 1.5}
                           ],

    'dataframe_adjustments': [["Revenge of the Cactus 1", "N/A", 9, 50000, 0],
                              ["Revenge of the Cactus 2", "2001-01-01", 8.5, 150000, 2],
                              ["Revenge of the Cactus 3", "2003-04-24", 7.2, 200000, 5],
                              ["Revenge of the Cactus 4", "2007-10-13", 5.7, 250000, 8],
                              ["Revenge of the Cactus 5", "2015-12-24", 3.2, 95613, 12]
                              ],

    'dataframe_adjustments_results': [["Revenge of the Cactus 1", "N/A", 9, 50000, 0, 8.8],
                                      ["Revenge of the Cactus 2", "2001-01-01", 8.5, 150000, 2, 8.7],
                                      ["Revenge of the Cactus 3", "2003-04-24", 7.2, 200000, 5, 7.7],
                                      ["Revenge of the Cactus 4", "2007-10-13", 5.7, 250000, 8, 6.7],
                                      ["Revenge of the Cactus 5", "2015-12-24", 3.2, 95613, 12, 4.6]
                                      ],

    'dataframe_to_csv': [["Revenge of the Cactus 1", "N/A", 9, 50000, 0, 8.8],
                         ["Revenge of the Cactus 2", "2001-01-01", 8.5, 150000, 2, 8.7],
                         ["Revenge of the Cactus 3", "2003-04-24", 7.2, 200000, 5, 7.7],
                         ["Revenge of the Cactus 4", "2007-10-13", 5.7, 250000, 8, 6.7],
                         ["Revenge of the Cactus 5", "2015-12-24", 3.2, 95613, 12, 4.6]
                         ]
}


