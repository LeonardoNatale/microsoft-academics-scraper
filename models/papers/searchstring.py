from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db
from sqlalchemy.orm import relationship


class SearchString(Base, BaseTable):

    __tablename__ = 'SearchString'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    pub_year_filter = db.Column(db.String)

    # Many to many with paper
    papers = relationship(
        "PaperHasSearchString",
        backref="search_string",
        cascade="save-update, merge, delete, delete-orphan"
    )

