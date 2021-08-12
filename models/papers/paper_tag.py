import sqlalchemy as db
from sqlalchemy.orm import relationship

from models.base import Base
from models.base_table import BaseTable


class PaperTag(Base, BaseTable):

    __tablename__ = "PaperTag"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    papers = relationship('PaperHasTag', backref='tag', cascade="save-update, merge, delete, delete-orphan")
