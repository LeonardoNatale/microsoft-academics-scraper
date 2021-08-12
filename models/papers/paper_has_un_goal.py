from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db


class PaperHasUNGoal(Base, BaseTable):

    __tablename__ = 'PaperHasUNGoal'

    paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), primary_key=True)
    un_goal_id = db.Column(db.Integer, db.ForeignKey('UNGoal.id'), primary_key=True)
    relevance = db.Column(db.String(10))  # TODO: populate this column.
