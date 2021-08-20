import itertools
from typing import List
import random

import pandas

from queries.ma_query import MAQuery


def generate_queries(data: pandas.DataFrame, nb_queries: int, nb_keywords: int = 2) -> List[MAQuery]:
    # TODO make sure we don't have twice the same query. (use itertools.combinations())
    return [generate_query(data=data, nb_keywords=nb_keywords) for i in range(nb_queries)]


def generate_query(data: pandas.DataFrame, nb_keywords: int = 3):
    """
    From a dataset with multiple columns, selects at random `nb_keywords` columns
    and returns a list of randomly picked keywords (one keyword per column)

    @param data: The dataset
    @param nb_keywords: The number of keywords to pick
    @return: A list of keywords randomly picked
    """
    columns = random.sample(list(data.columns), nb_keywords)
    return MAQuery(
        query=[random.choice(data[column].dropna().tolist()) for column in columns],
        columns=[x.strip() for x in columns]
    )


# TODO delete
def _generate_subqueries(start: str, options: set, nb_keywords: int) -> List[set]:
    return [
        {start, *words} for words in itertools.combinations(options, nb_keywords)
    ]


if __name__ == "__main__":
    pass
