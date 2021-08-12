import random
from typing import List

from research_apis.utils.query_builder import generate_queries
from scrapers.utils.ma_query import MAQuery


class QueryGenerator:
    AGRICULTURE_KEYWORDS = ['agriculture', 'agroforestry', 'agroecology']
    ADDITIONAL_QUERIES = ['carbon project agriculture', 'agriculture case study greenhouse gas']

    def __init__(self):
        pass

    @classmethod
    def get_search_strings(cls, nb_queries: int = 2, nb_keywords: int = 3) -> List[MAQuery]:
        ag_kw = cls.AGRICULTURE_KEYWORDS[random.randint(0, len(cls.AGRICULTURE_KEYWORDS) - 1)]
        nb_fixed_queries = nb_queries - len(cls.ADDITIONAL_QUERIES)
        fixed_queries = []
        if nb_fixed_queries > 0:
            queries = generate_queries(nb_queries=nb_fixed_queries, nb_keywords=nb_keywords)
            fixed_queries = [
                MAQuery(' '.join([ag_kw.capitalize()] + [x.replace('"', '').capitalize() for x in elm]), False)
                for elm in queries
            ]
        return ([MAQuery(q, True) for q in cls.ADDITIONAL_QUERIES] + fixed_queries)[:nb_queries]
