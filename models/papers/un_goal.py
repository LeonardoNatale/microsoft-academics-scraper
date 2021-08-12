from sqlalchemy.orm import relationship
from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db


class UNGoal(Base, BaseTable):

    __tablename__ = 'UNGoal'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    papers = relationship('PaperHasUNGoal', backref='un_goal')
