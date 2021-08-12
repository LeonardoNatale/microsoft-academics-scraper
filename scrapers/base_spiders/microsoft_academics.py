import os
from typing import List, Union, Dict, Optional
from datetime import datetime
import itertools
import time
import pandas as pd
import traceback

from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.keys import Keys

from models.db_session import DBSession
from research_apis.search_strings.arxiv_search_string import ArXivSearchString
from scrapers.base_spiders.base_paper_spider import BasePaperSpider
from scrapers.utils.driver_factory import DriverFactory
from scrapers.utils.ma_query import MAQuery
from scrapers.utils.query_generator import QueryGenerator


class MicrosoftAcademicsSpider(BasePaperSpider):
    QUERY_DATABASE = 'microsoft_academics'
    start_urls = ['https://academic.microsoft.com/home']

    def __init__(self, db_session: DBSession, page_limit: int = None, citation_count_filter: int = 5, timeout: int = 10,
                 max_queries: int = 2, headless: List[bool] = None, depth_limit: int = 0, pub_year_filter: int = 2005,
                 sub_page_citation_limit: int = 500, follow_recommendations: bool = False, csv_path: str = None,
                 **kwargs):
        super().__init__(db_session, page_limit, citation_count_filter, **kwargs)
        self.max_queries = max_queries
        self.depth_limit = depth_limit
        self.pub_year_filter = pub_year_filter
        self.sub_page_citation_limit = sub_page_citation_limit
        self.follow_recommendations = follow_recommendations
        self.csv_path = csv_path
        headless = headless or [False, False]
        self.logger.info('Getting the drivers...')
        self.driver = DriverFactory.get_driver(headless=headless[0], timeout=timeout)
        self.page_driver = DriverFactory.get_driver(headless=headless[1], timeout=timeout)
        self.logger.info('Drivers loaded.')

    def run(self):
        start_url = MicrosoftAcademicsSpider.start_urls[0]
        for search_string in QueryGenerator.get_search_strings(self.max_queries, 3):
            self.logger.info(f'Scraping data for the following search string: {search_string.query}')
            self.papers += self.parse(url=start_url, query=search_string)
        self.driver.quit()
        self.page_driver.quit()
        return self.insert_data()

    def parse(self, url: str, query: MAQuery) -> List[dict]:
        self.driver.get(url)
        self.page_count = 1
        papers = []
        try:
            # Wait for the search bar to be there and click on an element of the screen to make cookie bar disappear.
            self.driver.wait_and_click(
                func=ec.presence_of_element_located,
                css_class='suggestion-box',
                css_selector='div.ma-hp-info',
                ignore_exceptions=[False, False]
            )
            time.sleep(2)
            # Wait for the cookie bar to disappear (logo is visible)
            self.driver.wait_for_css_class(
                func=ec.element_to_be_clickable,
                css_class='hp-suggestions',
                ignore_exceptions=False
            )
            time.sleep(2)
            # Look for the search input, clear the content, click on it, send the search query.
            element = self.driver.find_elements_by_css_selector('div.suggestion-box > input#search-input')[1]
            element.click()
            element.send_keys(query.query)
            time.sleep(2)
            if self.follow_recommendations:
                # Wait for the suggestions to appear.
                self.driver.wait_for_css_class(
                    func=ec.visibility_of_element_located,
                    css_class='suggestion',
                    ignore_excptions=True
                )
                # Click on the first suggestion, else, if no suggestion, just send the query.
                try:
                    self.driver.find_elements_by_css_selector('ul > li.suggestion')[0].click()
                except (NoSuchElementException, IndexError):
                    element.send_keys(Keys.ENTER)
            else:
                element.send_keys(Keys.ENTER)
            # Wait for the list of papers to be there.
            self.driver.wait_for_papers_to_load()
            # Filtering by publication type.
            types = [
                (
                    # The box to tick conditionally
                    publication_type.find_element_by_css_selector('div.field > div.checkbox.shadowed > span.checkmark'),
                    # The actual publication type.
                    publication_type.find_element_by_css_selector('div.data > div.values > div.caption').text
                )
                for publication_type in self.driver.find_elements_by_css_selector(
                    'ma-publication-type-filter > compose > div.filter-card > div.data-bar-item.au-target > '
                    'ma-data-bar > div.au-target.ma-data-bar'
                )
            ]
            time.sleep(2)
            # Filter on Journal publications.
            for box, publication_type in types:
                if publication_type == 'Journal publications':
                    box.click()
            time.sleep(2)
            # Selecting the right date range (2010-present) and click ont he date range to display choices.
            self.driver.wait_and_click(
                func=ec.visibility_of_element_located,
                css_class='primary_paper',
                css_selector='div.au-target.ma-year-range-dropdown',
                ignore_exceptions=[False, True]
            )
            time.sleep(2)
            # Getting all the possible values.
            choices = self.driver.find_elements_by_css_selector('div.au-target.year-item')
            year_choices = [
                int(elm.find_element_by_css_selector('div.year-value').text) >= self.pub_year_filter
                for elm in choices
            ]
            choices = list(itertools.compress(choices, year_choices))
            if len(choices):
                choices[0].click()
                time.sleep(2)
                choices[-1].click()
                time.sleep(2)
            # Wait for the click to be done
            self.driver.wait_for_papers_to_load()
            # 1 is arbitrary value just so it's not None.
            next_page_element = 1
            while next_page_element is not None and (self.page_limit is None or self.page_count <= self.page_limit):
                papers += self.parse_paper_list(url=url, query=query)
                next_page_element = self.driver.get_next_page_link()
                self.driver.go_to_next_page(next_page_element=next_page_element)
                # self.parse_next_page(driver=driver, next_page_element=next_page_element)
            # driver.quit()
            return papers
        except (NoSuchElementException, TimeoutException):
            self.logger.warning(traceback.print_exc())
            # driver.quit()
            self.logger.warning('Nothing parsed on page.')
            return papers or []

    def parse_paper_list(self, url: str, query: MAQuery, depth: int = 0) -> Optional[List[dict]]:
        """
        Parses the list of papers on a given page.

        :param url: The URL to parse
        :param query: The query to fetch the paper.
        :param depth:
        :return: A list of papers as dict elements.
        """
        super().parse(url=url, query='')
        # Getting a list of tuples with the paper and its citation count.
        links_citations = list(zip(
            self.driver.get_href_list(css_string='div.primary_paper > a.title', ignore_exceptions=False),
            self.driver.get_text_list(
                css_string='div.citation > a > span',
                lambda_transform=lambda x: int(x.split()[0].replace(',', ''))
            )
        ))
        papers = [
            self.parse_paper(link=link, query=query, citation_count=citation, depth=depth)
            for link, citation in links_citations
        ]
        if papers:
            # Filtering out the None values.
            papers = list(itertools.chain(*list(filter(None, papers))))
            if papers:
                return papers
        return []

    def parse_paper(self, link: str, query: MAQuery, citation_count: int, depth: int = 0) -> Union[List[Dict], None]:
        super().parse_paper(link='', query=query.query, citation_count=citation_count, depth=depth)
        citation_filter = self.citation_count_filter if not query.is_project_oriented else -1
        if depth > 0:
            citation_filter = self.sub_page_citation_limit
        if citation_count < citation_filter or depth > self.depth_limit:
            return None
        # driver = DriverFactory.get_driver(headless=self.headless[1])
        self.page_driver.get(link)
        try:
            # Wait for the main section to be visible and expand the categories if possible.
            self.page_driver.wait_and_click(
                func=ec.visibility_of_element_located,
                css_class='name-section',
                css_selector='div.tag-cloud > div.show-more',
                ignore_exceptions=[False, True]
            )
            # Wait for the categories to be expanded and expand the authors if possible.
            self.page_driver.wait_and_click(
                func=ec.visibility_of_element_located,
                css_class='authors',
                css_selector='div.authors > div.show-more',
                ignore_exceptions=[False, True]
            )
            self.page_driver.wait_for_css_class(
                func=ec.visibility_of_element_located,
                css_class='authors',
                ignore_exceptions=False
            )
            # Get the data
            d = {
                'title': self.page_driver.get_text(css_string='div.name-section > div.name'),
                'publication_date': datetime(
                    year=int(self.page_driver.get_text(css_string='div.name-section > a.publication > span.year')),
                    month=1,
                    day=1
                ),
                'source': self.page_driver.get_text(css_string='div.name-section > a.publication > span.pub-name'),
                'doi': self.page_driver.get_text(
                    css_string='div.name-section > a.doiLink',
                    lambda_transform=lambda x: x.replace('DOI: ', '').strip(),
                    ignore_exceptions=True
                ),
                'abstract': self.page_driver.get_text(css_string='div.name-section > p'),
                'tags': self.page_driver.get_text_list(
                    css_string='ma-link-tag > a.ma-tag > div.text',
                    ignore_exceptions=True
                ),
                'authors': self.page_driver.get_text_list(
                    css_string='div.authors > div.author-item > a.author.link',
                    ignore_exceptions=True
                ),
                'url': self.page_driver.get_href(
                    css_string='div.ma-link-collection > a.ma-link-collection-item',
                    ignore_exceptions=True
                ),
                'citation_count': citation_count
            }
            sub_papers = []
            if depth < self.depth_limit:
                sub_papers = self.parse_paper_list(url=link, query=query, depth=depth + 1)
            return [MicrosoftAcademicsSpider.format_for_db(content=d, query=query)] + sub_papers
        except TimeoutException:
            self.logger.warning("Timed out waiting for page to load")
            return None
        except StaleElementReferenceException:
            print(traceback.print_exc())
            self.logger.warning("One element is stale.")
        except NoSuchElementException:
            print(traceback.print_exc())
            self.logger.warning('One element is missing from page.')
        finally:
            pass
            # driver.close()

    def insert_data(self) -> int:
        """
        Inserts all the data int the papers DB.

        :return: The number of papers inserted.
        """
        self.logger.info(f'Inserting {len(self.papers)} papers :')
        if len(self.papers) < 50:
            self.logger.info('\n'.join([paper['title'] for paper in self.papers]))
        if self.papers:
            insert_count = sum([int(self.insert_to_db(paper)[0]) for paper in self.papers if paper])
            self.session.session.commit()
            # TODO remove
            self.save_data_to_csv()
            return insert_count
        else:
            return 0

    def save_data_to_csv(self):
        pd.DataFrame([MicrosoftAcademicsSpider.format_for_csv(paper) for paper in self.papers])\
            .drop_duplicates(subset=['title'])\
            .to_csv(os.path.join(self.csv_path, self.QUERY_DATABASE, 'papers.csv'))

    @staticmethod
    def format_for_csv(d: dict) -> dict:
        """
        Formats the data for it to be exported to csv.
        :param d: The dictionary to format
        :return: The formatted dictionary.
        """
        d['tags'] = ','.join(d['tags'])
        d['authors'] = ','.join(d['authors'])
        d['search_string'] = d['search_string']['name']
        return d

    @staticmethod
    def format_for_db(content: dict, query: MAQuery) -> Optional[Dict]:
        """
        Adds the search string parameters to the data.
        :param content: The initial content.
        :param query: The query.
        :return: The formatted content.
        """
        if not content:
            return None
        search_string = ArXivSearchString()
        search_string.clear()
        search_string.name = query
        return {
            **content,
            'search_string': {
                'name': query.query
            }
        }
