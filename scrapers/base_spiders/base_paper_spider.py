from abc import abstractmethod
from typing import Union, Tuple

from scrapers.base_spiders.base_spider import BaseSpider
from models.db_session import DBSession


class BasePaperSpider(BaseSpider):

    def __init__(self, db_session: DBSession, page_limit: int = None, citation_count_filter: int = 5, **kwargs):
        super().__init__(db_session=db_session, page_limit=page_limit, **kwargs)
        self.paper_count = 0
        self.citation_count_filter = citation_count_filter
        self.papers = []

    @property
    @abstractmethod
    def QUERY_DATABASE(self):
        """
        The name of the queried page.
        """
        raise NotImplementedError('This property should have a value.')

    @abstractmethod
    def run(self):
        super().run()

    def parse(self, url: str, query: str):
        super().parse(url=url, query=query)

    def parse_paper(self, link: str, query: str, citation_count: int):
        """
        Function to parse the content of a project, to be called from `parse()`.

        :param link: The link to the paper to parse.
        :param query: The search string
        :param citation_count: The citation count of the paper.
        :return: The result of the parsing.
        """
        self.logger.info(f' > PARSING PAPER NUMBER ({self.paper_count})')
        self.paper_count += 1

    def insert_data(self) -> int:
        return super().insert_data()

    def insert_to_db(self, content: dict) -> Tuple[bool, Union[str, None]]:
        """
        Inserts a project to the project DB.
        :param content: The content of the article to insert.
        :return: a tuple with a boolean indicating whether the article has been added and an eventual error message.
        """
        return self.session.insert_to_papers_db(
            content={
                **content,
                'database': self.QUERY_DATABASE
            }
        )
