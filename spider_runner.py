import os
import models.base as base
from models.db_session import DBSession

from scrapers.base_spiders.microsoft_academics import MicrosoftAcademicsSpider

from spiders_config import CONFIG
from logzero import logger
from time import time


class SpiderRunner:
    SPIDERS = [
      MicrosoftAcademicsSpider
    ]

    def __init__(self):
        self.spiders_config = CONFIG.get('spiders')
        self.session = SpiderRunner.db_setup()
        self.logger = logger
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in os.environ['PATH'].split(os.pathsep):
            self.logger.info(f'Appending path to geckodriver executable ({current_dir}) to PATH')
            os.environ["PATH"] += os.pathsep + current_dir

    def run(self):
        """
        Runs the spiders with their associated configuration provided in `CONFIG_FILE`
        For every Spider, a process is created and the method crawl() is called.

        :return:
        """
        total_papers_inserted = 0
        if SpiderRunner.SPIDERS:
            for spider in SpiderRunner.SPIDERS:
                spider_config = self.spiders_config.get(spider.__name__)
                if spider_config:
                    start = time()
                    papers_inserted = spider(**{**spider_config, 'db_session': self.session}).run()
                    self.logger.info(f'Inserted {papers_inserted} papers(s) for {spider.__name__}. in {time() - start}')
                    total_papers_inserted += papers_inserted
                else:
                    raise KeyError(f'No config found for spider {spider.__name__} in config.')
        self.close_db()
        self.logger.info(f'Inserted {total_papers_inserted} papers in total.')

    @staticmethod
    def db_setup():
        """
        Instantiates a db session object and does some pre-processing on the DB.

        :return: A session object.
        """
        session = base.get_session()
        # TODO DELETE when we have a proper running system.
        tables = base.get_tables().keys()
        for table in tables:
            session.execute(f"DELETE FROM {table};")
            session.commit()
        return DBSession(session)

    def close_db(self):
        if self.session:
            self.session.session.close()


sr = SpiderRunner()
sr.run()
