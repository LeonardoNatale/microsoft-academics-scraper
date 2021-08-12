import urllib
import feedparser
from models.db_session import DBSession
from models.papers.paper import Paper
from research_apis.database_apis.base_research_query import BaseResearchQuery
from research_apis.search_strings.arxiv_search_string import ArXivSearchString
from datetime import datetime

from research_apis.utils.get_paper_info import get_doi_from_title, get_source_from_doi


class ArXivQuery(BaseResearchQuery):

    KEYS = ['title', 'authors', 'links', 'link', 'published', 'summary', 'tags', 'arxiv_doi']
    MAPPING = {
        'link': 'url',
    }
    QUERY_DATABASE = 'arxiv'
    REQUIRED_ATTRIBUTES = [*Paper.get_attributes(), 'searchstring', 'source', 'authors']

    def __init__(self, db_session: DBSession, nb_queries: int = 10, paper_limit_per_query: int = None):
        super().__init__(db_session=db_session)
        self.papers = []
        self.nb_queries = nb_queries
        self.paper_limit_per_query = paper_limit_per_query

    def _set_search_strings(self) -> None:
        for i in range(self.nb_queries):
            search_string = ArXivSearchString(self.paper_limit_per_query)
            search_string.generate_search_string()
            while search_string in self.search_strings:
                print(f"Query was already drawn.")
                search_string = ArXivSearchString(self.paper_limit_per_query)
                search_string.generate_search_string()
            self.search_strings.append(search_string)

    def set_data(self) -> None:
        for q in self.search_strings:
            # TODO remove
            q = ArXivSearchString.get_sample_ss()
            self.papers += [
                ArXivQuery.format_for_db(element, q)
                for element
                in feedparser.parse(urllib.request.urlopen(q.get_query_from_search_string()).read())['entries']
            ]

    def insert_data(self) -> int:
        return sum([int(self.session.insert_to_papers_db(content=paper)[0]) for paper in self.papers])

    @classmethod
    def format_for_db(cls, out: dict, ss: ArXivSearchString) -> dict:
        """
        Foramts the
        :param out:
        :param ss:
        :return:
        """
        return {
            **ArXivQuery.format_query_output({k: v for k, v in out.items() if k in cls.KEYS}),
            'search_string': ss.JSON(),
            'database': cls.QUERY_DATABASE
        }

    @classmethod
    def format_query_output(cls, out: dict) -> dict:
        out['title'] = ' '.join(out['title'].replace('\n', '').split())
        out['tags'] = [x['term'] for x in out['tags']]
        out['abstract'] = out.pop('summary').replace('\n', ' ')
        out['publication_date'] = datetime.strptime(out.pop('published').split('T')[0], '%Y-%m-%d')
        out['doi'] = out.pop('arxiv_doi', None)
        out['authors'] = [x['name'] for x in out['authors']]
        links = out.pop('links')
        if out['doi'] is None:
            extract = [
                x['href'].replace('http://dx.doi.org', '')
                for x in links
                if 'title' in x and x['title'] == 'doi'
            ]
            if len(extract):
                out['doi'] = extract[0]
        if out['doi'] is None:
            try:
                out['doi'] = get_doi_from_title(out['title'])
            except RuntimeError:
                pass
        out['source'] = get_source_from_doi(out['doi'])
        for k, v in ArXivQuery.MAPPING.items():
            out[v] = out.pop(k)
        print(out)
        return {k: v for k, v in out.items() if k in ArXivQuery.REQUIRED_ATTRIBUTES}
