import sqlalchemy as db
from sqlalchemy.orm import relationship

from models.base import Base
from models.base_table import BaseTable


class PaperHasSearchString(Base, BaseTable):

    __tablename__ = 'PaperHasSearchString'

    paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), primary_key=True)
    search_string_id = db.Column(db.Integer, db.ForeignKey('SearchString.id'), primary_key=True)
