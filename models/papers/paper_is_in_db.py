import sqlalchemy as db
from sqlalchemy.orm import relationship

from models.base import Base
from models.base_table import BaseTable


class PaperIsInDB(Base, BaseTable):
    __tablename__ = 'PaperIsInDB'
    paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), primary_key=True)
    db_id = db.Column(db.Integer, db.ForeignKey('ResearchDB.id'), primary_key=True)
