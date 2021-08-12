import requests
import time
import pandas as pd
import numpy as np
from typing import List
import random
import itertools
import logzero
import logging
from logzero import logger
from research_apis.utils.get_paper_info import get_info_from_doi
logzero.loglevel(logging.INFO)


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

def generate_searchstring_list(nb_queries: int=3):
    keywords = generate_queries(nb_queries, 2)
    print(len(["(agri OR agro) AND "+' '.join(tups) for tups in keywords]))
    return ["(agri OR agro) AND "+' '.join(tups) for tups in keywords]

def generate_headers(api_key: str = 'cba4d5664b436e110288e9ee208ffa6c'):  # Sarah's API key
    """
    Generates the authentication headers to enter as a parameter in PUT requests to Elsevier.
    :param api_key: token given by Elsevier to private account holders
    :return: a json dictionary containing an authentication token and the query response format
    """
    return {
        "Accept": "application/json",
        "X-ELS-APIKey": api_key,
        'Content-Type': 'application/json',
    }

def generate_json(show: int = 100, offset: int = 0, pub_year_filter: str="2005-2020", name: str =""):
    """
    Generates the json query body to enter as a parameter in PUT requests to Elsevier.
    :param show: Accepted values: 25, 50, 100. The number of results to show by query.
    :param offset: Accepted values: 0-6000. The position from which search results begin.
    :return: a json query dictionary containing the query body
    """
    return {
        'date': pub_year_filter,
        'qs': name,
        "display": {
            "offset": offset,
            "show": show,
            "sortBy": "relevance"
        },
    }


def send_put_request(json: dict, headers: dict, counter : int, url: str = 'https://api.elsevier.com/content/search/sciencedirect',
                     delay: int = 2, truncate: int = 3000):
    """
    Sends PUT request to the Elsevier API to retrieve full query results as a list of dictionaries.
    :param json: json query dictionary containing the query body
    :param headers: a json dictionary containing an authentication token and the query response format
    :param url: the API url to query
    :param delay: the number of seconds to wait in between each request
    :return: a json query results
    """
    logger1 = logger
    results = []
    offset = 0
    logger1.info(f"Query {counter}: {json['qs']}")
    counter = 1
    r = requests.put(url, json=json, headers=headers)
    time.sleep(delay)
    if r.status_code == 429:
        logger1.info(f" {counter} : request failed, status code {r.status_code}.")
        nb_results = 0
    else:
        logger1.info(f" {counter} : request successful, status code {r.status_code}.")
        r = r.json()
        if r.get('results', None):
            nb_results = r['resultsFound']
            results = r['results']
            logger1.info(f"Total results: {nb_results}.")
        else:
            nb_results = 0
            logger1.info('Empty set.')
    nb_to_retrieve = min(nb_results, truncate)
    for i in np.arange((nb_to_retrieve - nb_to_retrieve % 100) / 100):
        offset += 100
        counter += 1
        json['display']['offset'] = str(offset)
        r = requests.put(url, json=json, headers=headers)
        time.sleep(delay)
        if r.status_code == 429:
            logger1.info(f"{counter} : request failed, status code {r.status_code}.")
        else:
            logger1.info(f"{counter} : request successful, status code {r.status_code}.")
            r = r.json()
            if r.get('results', None):
                results.extend(r['results'])
    logger1.info(f"Extracted results: {len(results)}.")
    return results


def get_additional_paper_info(doi, api_key):
    info = {}
    url = "https://api.elsevier.com/content/article/doi/"
    r = requests.get(url=(url + doi), headers=generate_headers(api_key))
    r = r.json()['full-text-retrieval-response']

    # Fulltext
    info["fulltext"] = r.get('originalText', None)
    if type(info["fulltext"]) == dict:
        info["fulltext"] = None

    ## Dive one step further
    r = r['coredata']
    # Tags
    info["tags"] = r.get('dcterms:subject', None)
    if info["tags"]:
        info["tags"] = [list(d.values())[1] for d in info["tags"]]
    # Publication type
    info["pub_type"] = r.get("pubType", None)
    # Content type
    info["content_type"] = r.get('prism:aggregationType', None)
    # Abstract
    info["abstract"] = r.get('dc:description', None)
    # Citation count (retrieved using crossref)
    info["citation_count"] = get_info_from_doi(doi).get("citation-count", None)
    return info

def remove_duplicates(my_dict_list: List[dict]):
    """
    Remove result search duplicates by scanning for identical dictionaries.
    Does not remove identical papers with different search strings.
    :param my_dict_list: list of dictionaries to remove duplicates for.
    :return:
    """
    return [i for n, i in enumerate(my_dict_list) if i not in my_dict_list[n + 1:]]


def standardise_papers(results: List[dict], search_string: dict, truncate : int =10):
    """
    Format search results from Elsevier to fit our database models.
    :param results: list of dictionaries, each one corresponding to a paper
    :param search_string: The search string object.
    :return: list of dictionaries, each one corresponding to a standardised paper ready to insert into the DB.
    """
    logger1 = logger
    my_categories = {
        "title": "title",
        "authors": "authors",
        "loadDate": "publication_date",
        "sourceTitle": "source",
        "doi": "doi",
        "uri": "url",
        "search_string": "search_string",
        "abstract": "abstract",
        "database": "database",
    }
    # Extract relevant keys and rename them
    papers = []
    for result in results[:truncate]:
        authors = result.get('authors', None)
        result["authors"] = [r['name'] for r in authors] if authors else None
        result['search_string'] = search_string
        result['abstract'] = None
        result['database'] = "sciencedirect"
        result['loadDate'] = pd.to_datetime(result['loadDate'])
        # Extract only relevant keys from result
        temp = {your_key: result.get(your_key, None) for your_key in my_categories.keys()}
        # Rename the keys
        paper = dict(zip(map(lambda x: my_categories[x], temp.keys()), temp.values()))
        papers.append(paper)
    logger1.info(f"{len(papers)} papers retrieved.")
    return papers[:truncate]


def get_abstracts_fulltext_tags(contents, api_key):
    """
    Retrieves additional information once per paper by using the doi as a unique identifier.
    If a paper was already encountered, retrieves the information directly from a local dictionary.
    :param contents: list of dictionaries, each representing a paper
    :param api_key: The API key.
    :return: list of dictionaries, each representing a paper and its abstract when available.
    """
    logger1 = logger
    info = {}
    counter = 0
    redundant_paper_counter = 0
    wrong_content_paper_counter = 0
    for content in contents:
        counter += 1
        doi = content.get('doi', None)
        if doi:  # if there is a doi
            # Check whether paper was already encountered
            # And initialize content info in consequence.
            if info.get(doi, None):
                logger1.info(f"Information for paper {counter} had already been retrieved.")
                redundant_paper_counter += 1
                # If so, fill in your content using the previously retrieved information.
                content_info = info[doi]
            else:
                logger1.info(f" Retrieving additional information for paper {counter} / {len(contents)}.")
                content_info = get_additional_paper_info(doi, api_key)
                info[doi] = content_info # increment your info dictionary with the doi

            # Get the publication type
            # Check it is in the list of contents we allow
            if content_info.get("pub_type", None) in set(["rev", "fla", "crp", "chp", "dat"]):
                content['pub_type'] = content_info.get("pub_type", None)
                content['content_type'] = content_info.get("content_type", None)
                content['tags'] = content_info.get("tags", None)
                content['full_text'] = content_info.get("full_text", None)
                content['abstract'] = content_info.get("abstract", None)
                if content["abstract"]:
                    # Clean the abstract
                    content['abstract'] = "".join(content["abstract"].replace("Abstract", "").strip().split("\n"))
                content["citation_count"] = content_info.get("citation_count", None)
            else:
                # If the publication type isn't in our targets
                # Remove it from the contents
                logger1.info(f"Content type out of bounds: did not retrieve more information for paper {counter}.")
                content['pub_type'] = content_info.get("pub_type", None)
                wrong_content_paper_counter += 1
        else:
            logger1.info(f"Doi was None, preventing further information retrieval.")
    logger1.info(f"Retrieved {redundant_paper_counter} / {len(contents)} redundant papers in between queries." )
    logger1.info(f"Retrieved {wrong_content_paper_counter} / {len(contents)} papers with the wrong content type.")
    return contents



