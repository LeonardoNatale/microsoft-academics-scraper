from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db
from sqlalchemy.orm import relationship


class ResearchDB(Base, BaseTable):

    __tablename__ = 'ResearchDB'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    # Many to many with paper
    papers = relationship("PaperIsInDB", backref="database", cascade="save-update, merge, delete, delete-orphan")
