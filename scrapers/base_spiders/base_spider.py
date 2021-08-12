from abc import abstractmethod
from typing import Union
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from logzero import logger
from models.db_session import DBSession


class BaseSpider:
    """
    Base class for spiders implementing a set of methods that will be used (and overridden) by all spiders.
    """

    def __init__(self, db_session: DBSession, page_limit: int = None, *args, **kwargs):
        """
        Constructor of the BaseSpider class.

        :param db_session: The database session.
        :param page_limit: The maximum number of pages that should be parsed.
        """
        self.logger = logger
        self.logger.info(f' > Running Spider {self.__class__.__name__}')
        self.session = db_session
        self.page_count = 1
        self.page_limit = page_limit

    @abstractmethod
    def run(self) -> int:
        """
        Runs the spider, crawls the pages and inserts the content to the DB.
        :return: The number of rows inserted during the run.
        """
        raise NotImplementedError('You should implement this method.')

    def parse(self, url: str, query: str):
        """
        Parse method of the spider.

        :param url: The URL to parse
        :param query: The query to use on the page.
        :return: The result of the parsing.
        """
        self.logger.info(f' > PARSING PAGE {self.page_count}')
        self.logger.info(f' > URL : {url}')
        self.page_count += 1

    @abstractmethod
    def insert_data(self) -> int:
        """
        Inserts data into the DB.

        :return: The number of rows inserted.
        """
        raise NotImplementedError('You should implement this method.')
