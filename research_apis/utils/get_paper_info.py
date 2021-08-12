from typing import Union
import signal
from habanero import Crossref, counts
from requests import HTTPError

cr = Crossref()


def get_info_from_doi(doi: str) -> dict:
    """
    :param doi: unique identifier.
    :return: dictionary with all quantitative info + subject
    """

    signal.signal(signal.SIGALRM, handler)  # register interest in SIGALRM events
    signal.alarm(1)  # timeout in 2 seconds
    try:
        response = cr.works(ids=doi)
    except:# (Timeout, HTTPError, ConnectionError):
        return {}

    if response.get("status") != "ok":
        raise RuntimeError("Error when retrieving the data")
    message = response.get("message")
    d = {"references-count": message.get("references-count"),
         "reference-count": message.get("reference-count"),
         "is-referenced-by-count": message.get("is-referenced-by-count"),
         "score": message.get("score"),
         "subject": message.get("subject")}
    try:
        d["citation-count"] = int(counts.citation_count(doi=doi))
    except:
        d["citation-count"] = None

    return d


def get_doi_from_title(title: str) -> Union[str, None]:
    """
    Returns the DOI of an article given it's title.

    :param title: The title of the article
    :return: The DOI of the article
    """
    response = cr.works(query=title, limit=1)
    if response.get("status") != "ok":
        raise RuntimeError("Error when retrieving the data")
    items = response["message"]["items"]
    if len(items):
        message = items[0]
        if message.get('title') is not None and (message.get("title")[0]).lower() == title.lower():
            return message.get("DOI")
    return None


def get_source_from_doi(doi: str) -> Union[str, None]:
    """
    Returns te journal the paper was published in given the DOI

    :param doi: The DOI of the paper.
    :return: The journal in which the paper was published.
    """
    if doi is None:
        return None
    response = cr.works(ids=doi)
    if response.get("status") != "ok":
        raise RuntimeError("Error when retrieving the data")
    message = response.get("message")
    if message.get("container-title"):
        return message.get("container-title")[0]
    return None


def get_type_from_doi(doi: str) -> dict:
    """
    :param doi: unique identifier.
    :return: dictionary with the publication type.
    """

    signal.signal(signal.SIGALRM, handler)  # register interest in SIGALRM events
    signal.alarm(1)  # timeout in 2 seconds
    try:
        response = cr.works(ids=doi)
    except (Timeout, HTTPError):
        return {}

    if response.get("status") != "ok":
        raise RuntimeError("Error when retrieving the data")
    message = response.get("message")
    return {
        "type": message.get("type")
    }


class Timeout(Exception):
    pass


def handler(sig, frame):
    pass
