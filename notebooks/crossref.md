# Crossref API


## Getting number of citations

```python
import json
import crossref_commons.retrieval
from crossref_commons.relations import get_related
```

```python
doi = "10.1016/j.esd.2019.02.001"
```

```python
response = crossref_commons.retrieval.get_publication_as_json(doi)
print(json.dumps(response, indent=2))
```

### Retrieving relations

```python
get_related("10.1016/j.aeae.2014.03.007")
```

___


# Habanero API for Crossref

```python
from habanero import Crossref, counts
```

```python
counts.citation_count("10.1016/j.esd.2019.02.001")
```

```python
cr = Crossref()
```

```python
response = cr.works(ids=doi)
message = response.get("message")
print(json.dumps(message, indent=2))
```

Getting citation info:

```python
def get_info_from_doi(doi: str):
    info = {}
    response = cr.works(ids=doi)
    if response.get("status") != "ok":
        raise Exception("Error when retrieving the data")
    message = response.get("message")
    info["references-count"] = message.get("references-count")
    info["reference-count"] = message.get("reference-count")
    info["is-referenced-by-count"] = message.get("is-referenced-by-count")
    info["score"] = message.get("score")
    info["subject"] = message.get("subject")
    info["citation-count"] = counts.citation_count(doi=doi)
    return info
```

```python
get_info_from_doi(doi)
```

Getting DOI from title:

```python
def get_doi_from_title(title: str):
    response = cr.works(query=title, limit=1)
    if response.get("status") != "ok":
        raise Exception("Error when retrieving the data")
    message = response["message"]["items"][0]
    if (message.get("title")[0]).lower() == title.lower():
        return message.get("DOI")
    return ""
```

```python
query = {
    'query.title': 'Credit Calibration with Structural Models: The Lehman case and Equity Swaps under Counterparty Risk'
}
```

```python
response = cr.works(query=query)
message = response["message"]
message
```

```python
get_doi_from_title("Credit Calibration with Structural Models: The Lehman case and Equity Swaps under Counterparty Risk")
```

---

```python
def get_source_from_doi(doi: str):
    response = cr.works(ids=doi)
    if response.get("status") != "ok":
        raise RuntimeError("Error when retrieving the data")
    message = response.get("message")
    if message.get("container-title"):
        return message.get("container-title")[0]
    return None
```

```python
get_source_from_doi("10.1111/gcb.14503")
```
