from sqlalchemy.orm import relationship

from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db


class AuthorWritesPaper(Base, BaseTable):

    __tablename__ = 'AuthorWritesPaper'

    paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('PaperAuthor.id'), primary_key=True)
