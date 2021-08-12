from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db
from sqlalchemy.orm import relationship


class PaperAuthor(Base, BaseTable):

    __tablename__ = 'PaperAuthor'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    # Many to many with paper
    papers = relationship(
        "AuthorWritesPaper",
        backref="paper_author",
        cascade="save-update, merge, delete, delete-orphan"
    )
