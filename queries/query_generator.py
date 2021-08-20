import random
from typing import List

import pandas

from queries.ma_query import MAQuery
import pandas as pd
import os


class MicrosoftAcademicsQueryGenerator:
    ADDITIONAL_QUERIES = []

    def __init__(self):
        pass

    @classmethod
    def get_search_strings(cls, keyword_file: str, nb_queries: int = 2, nb_keywords: int = 3) -> List[MAQuery]:
        """
        Returns a list of search strings from a keyword file.

        @param keyword_file: Name of the keyword file
        @param nb_queries: number of queries to generate
        @param nb_keywords: number of keywords per query
        @return:
        """
        keywords = pd.read_csv(filepath_or_buffer=os.path.join('keywords', keyword_file))
        nb_fixed_queries = nb_queries - len(cls.ADDITIONAL_QUERIES)
        queries = []
        if nb_fixed_queries > 0:
            queries = [cls.generate_query(data=keywords, nb_keywords=nb_keywords) for _ in range(nb_queries)]
        return ([MAQuery(q, [None] * nb_keywords) for q in cls.ADDITIONAL_QUERIES] + queries)[:nb_queries]

    @classmethod
    def generate_query(cls, data: pandas.DataFrame, nb_keywords: int = 3):
        """
        From a dataset with multiple columns, selects at random `nb_keywords` columns
        and returns a list of randomly picked keywords (one keyword per column)

        @param data: The dataset
        @param nb_keywords: The number of keywords to pick
        @return: A list of keywords randomly picked
        """
        columns = random.sample(list(data.columns), nb_keywords)
        return MAQuery(
            query=[random.choice(data[column].dropna().tolist()).strip() for column in columns],
            columns=[x.strip() for x in columns]
        )


if __name__ == "__main__":
    MicrosoftAcademicsQueryGenerator.get_search_strings("keywords_en.csv")
