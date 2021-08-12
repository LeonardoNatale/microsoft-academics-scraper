from models.db_session import DBSession
from research_apis.db_config import DB_CONFIG
from abc import abstractmethod
from logzero import logger


class BaseResearchQuery:

    def __init__(self, db_session: DBSession):
        self.session = db_session
        self.config = DB_CONFIG
        self.logger = logger
        self.search_strings = []

    @property
    @abstractmethod
    def QUERY_DATABASE(self):
        raise NotImplementedError('Class should have this attribute.')

    def run(self) -> int:
        """
        Runs the data extraction, transformation and loading into the DB.
        """
        self._set_search_strings()
        self.set_data()
        return self.insert_data()

    @abstractmethod
    def _set_search_strings(self):
        """
        Sets the search strings up.
        """
        raise NotImplementedError('Function should be implemented')

    @abstractmethod
    def set_data(self):
        """
        Gets the data from the APIs and transforms it.
        """
        raise NotImplementedError('Function should be implemented')

    @abstractmethod
    def insert_data(self) -> int:
        """
        Inserts the data to the DB.
        """
        raise NotImplementedError('Function should be implemented')
