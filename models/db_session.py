from typing import List, Any, Tuple, Union

from sqlalchemy.orm import Session

# Papers imports
from models.papers.paper import Paper
from models.papers.author import PaperAuthor
from models.papers.researchdb import ResearchDB
from models.papers.searchstring import SearchString
from models.papers.source import Source
from models.papers.un_goal import UNGoal
from models.papers.author_writes_paper import AuthorWritesPaper
from models.papers.paper_has_searchstring import PaperHasSearchString
from models.papers.paper_is_in_db import PaperIsInDB
from models.papers.paper_has_tag import PaperHasTag
from models.papers.paper_tag import PaperTag
from models.papers.paper_has_un_goal import PaperHasUNGoal
from logzero import logger
import pprint


class DBSession:

    def __init__(self, session: Session, batch_size=100):
        self.session = session
        self.logger1 = logger
        self.logger = self.logger1
        self.batch_size = batch_size
        self.paper_batch_counter = 0
        self.transaction_batch_counter = 0

    @staticmethod
    def fill_missing_content(content: dict, required_attributes: list) -> dict:
        """
        Given a dictionary and a list of keys, creates the keys that are
        missing in dictionary from the list and assign them the value None.

        :param content: The dictionary to be completed.
        :param required_attributes: The attributes that the dictionary must contain.
        :return: The filled dictionary.
        """
        diff = [x for x in required_attributes if x not in set(content)]
        for key in diff:
            content[key] = None
        return content

    def insert_to_papers_db(self, content: dict) -> Tuple[bool, Union[str, None]]:
        # TODO: check with doi
        if content.get('doi', None) and Paper.row_exists(session=self.session, title=content['doi']):
            return False, content.get('title')
        else:
            # Many to one where source is parent
            source = Source.get_object(session=self.session, name=content.get('source'))
            if source:
                content["source"] = source
            database = [content.pop('database', None)]
            paper_authors = content.pop('authors', None)
            tags = content.pop('tags', None)
            search_string_content = content.pop("search_string", None)
            un_goals = content.pop('un_goals', None)
            paper = Paper.get_object(self.session, restrict_search_kwargs=['title'], **content)
            # Add to DB
            search_string = SearchString.get_object(self.session, **search_string_content)
            paper_has_search_string = PaperHasSearchString.get_object(
                self.session,
                paper=paper,
                search_string=search_string
            )
            paper.search_strings.append(paper_has_search_string)
            self.session.add(paper)

            paper.databases = DBSession.get_many_to_many_objects_paper(
                elements=database,
                relation=PaperIsInDB,
                child=ResearchDB,
                param='database',
                search_param='name',
                session=self.session,
                paper=paper
            )

            paper.paper_authors = DBSession.get_many_to_many_objects_paper(
                elements=paper_authors,
                relation=AuthorWritesPaper,
                child=PaperAuthor,
                param='paper_author',
                search_param='name',
                session=self.session,
                paper=paper
            )

            paper.tags = DBSession.get_many_to_many_objects_paper(
                elements=tags,
                relation=PaperHasTag,
                child=PaperTag,
                param='tag',
                search_param='name',
                session=self.session,
                paper=paper
            )

            paper.un_goals = DBSession.get_many_to_many_objects_paper(
                elements=un_goals,
                relation=PaperHasUNGoal,
                child=UNGoal,
                param='un_goal',
                search_param='name',
                session=self.session,
                paper=paper
            )
            if self.paper_batch_counter > self.batch_size:
                self.session.commit()
                self.paper_batch_counter = 0
            else:
                self.paper_batch_counter += 1
            return True, None

    @staticmethod
    def get_dict_attributes(d: dict, attr: List[str]) -> dict:
        """
        Extracts the elements of the dict d whose keys belong to attr.

        :param d: The dict to extract keys from.
        :param attr: The attributes to search for in the dict.
        :return: The filtered dict.
        """
        return {
            key: d[key]
            for key in [  # Getting the keys that are project_related.
                key for key in d.keys()
                if key in attr
            ]
        }

    @staticmethod
    def get_many_to_many_objects_paper(elements: List[str], relation, child, param: str,
                                       search_param: str, session: Session, paper: Paper) -> List[Any]:
        if elements:
            return [
                relation.get_object(
                    session=session,
                    **{
                        'paper': paper,
                        param: child.get_object(session=session, **{search_param: elm})
                    }
                )
                for elm in elements
            ]
        else:
            return []

    @property
    def batch_size(self):
        return self.__batch_size

    @batch_size.setter
    def batch_size(self, value):
        self.__batch_size = value
