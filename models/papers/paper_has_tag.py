from sqlalchemy.orm import relationship

from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db


class PaperHasTag(Base, BaseTable):

    __tablename__ = "PaperHasTag"

    paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('PaperTag.id'), primary_key=True)
