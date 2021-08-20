from typing import List

from queries.query_builder import generate_queries
from queries.ma_query import MAQuery
import pandas as pd
import os


class MicrosoftAcademicsQueryGenerator:
    ADDITIONAL_QUERIES = []

    def __init__(self):
        pass

    @classmethod
    def get_search_strings(cls, keyword_file: str, nb_queries: int = 2, nb_keywords: int = 3) -> List[MAQuery]:
        keywords = pd.read_csv(filepath_or_buffer=os.path.join('keywords', keyword_file))
        nb_fixed_queries = nb_queries - len(cls.ADDITIONAL_QUERIES)
        queries = []
        if nb_fixed_queries > 0:
            queries = generate_queries(data=keywords, nb_queries=nb_fixed_queries, nb_keywords=nb_keywords)
        return ([MAQuery(q, [None] * nb_keywords) for q in cls.ADDITIONAL_QUERIES] + queries)[:nb_queries]


if __name__ == "__main__":
    MicrosoftAcademicsQueryGenerator.get_search_strings("keywords_en.csv")
