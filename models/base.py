from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('sqlite:///papers.db')
_SessionFactory = sessionmaker(bind=engine)


def get_session():
    """
    Generates a new session for the database.

    :return: The session object.
    """
    Base.metadata.create_all(engine)
    return _SessionFactory()


def get_tables():
    return Base.metadata.tables
