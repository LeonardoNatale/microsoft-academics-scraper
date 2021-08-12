import itertools
from typing import List
import random


def generate_queries(nb_queries: int, nb_keywords: int = 2) -> List[set]:
    starting_set = {"carbon", "\"greenhouse gas\"", "emissions"}
    all_set = {"carbon", "\"greenhouse gas\"", "emissions", "mitigation",
               "offset", "market", "trade", "permit", "credit"}
    keywords = []
    for i in starting_set:
        temp = all_set.copy()
        temp.remove(i)
        [keywords.append(query) for query in _generate_subqueries(i, temp, nb_keywords) if query not in keywords]
    if nb_queries >= len(keywords):
        return keywords
    return random.sample(keywords, k=nb_queries)


def _generate_subqueries(start: str, options: set, nb_keywords: int) -> List[set]:
    return [
        {start, *words} for words in itertools.combinations(options, nb_keywords)
    ]


if __name__ == "__main__":
    print(generate_queries(100, 6))
