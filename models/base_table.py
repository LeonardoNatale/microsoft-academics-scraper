from typing import List

from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.sql.expression import desc


class BaseTable:

    def __init__(self, **kwargs):
        # Setting the value of all the class attributes.
        for key, val in kwargs.items():
            setattr(self, key, val)

    @classmethod
    def search(cls, session: Session, **kwargs):
        """
        Returns the first row matching the search arguments passed in kwargs

        :param session: The database session.
        :param kwargs: The search arguments.
        :return: The first row as an object if there's a match, None otherwise.
        """
        return session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def row_exists(cls, session: Session, **kwargs):
        """
        Check if at least one row exists for the given search parameters.

        :param session: The database session.
        :param kwargs: The search arguments.
        :return: True if at least one row is found, False otherwise.
        """
        return session.query(cls).filter_by(**kwargs).count() > 0

    @classmethod
    def to_dataframe(cls, session: Session, **kwargs):
        """
        Returns the result of the query as a pandas DataFrame.

        :param session: The database session.
        :param kwargs: The search arguments.
        :return: The result of the query as a pandas DataFrame.
        """
        query = session.query(cls).filter_by(**kwargs)
        return pd.read_sql(query.statement, session.bind)

    @classmethod
    def get_object(cls, session: Session, flush: bool = False, restrict_search_kwargs: List[str] = None, **kwargs):
        """
        Returns the object if it exists in the db, otherwise it instantiates a new abject and returns it.
        NB : If any of the search parameters in None, returns None.

        :param session: The database session.
        :param flush: Should the object be flushed to the db after insertion.
        :param kwargs: The search/init arguments.
        :param restrict_search_kwargs: Restrict the search for duplicates to some fields of the kwargs only
        :return: A row of the table, either an existing one or a newly created one.
        """
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        search_kwargs = kwargs.copy()
        if not kwargs:
            return None
        if restrict_search_kwargs:
            search_kwargs = {k: v for k, v in search_kwargs.items() if k in restrict_search_kwargs}
        s = cls.search(session=session, **search_kwargs)
        if s:
            return s
        else:
            obj = cls(**kwargs)
            session.add(obj)
            if flush:
                session.flush()
            return obj

    @classmethod
    def get_attributes(cls, remove_id=True):
        """
        Returns the database column names.

        :param remove_id: Should the column `id` be removed?
        :return: The column names of the table.
        """
        lst = [elm.name for elm in inspect(cls).c]
        if remove_id:
            lst.remove('id')
        return lst

    @classmethod
    def search_column_max(cls, session: Session, column: str):
        return getattr(session.query(cls).order_by(desc(column)).first(), column)

