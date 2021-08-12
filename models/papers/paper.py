from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db
from sqlalchemy.orm import relationship


class Paper(Base, BaseTable):
    __tablename__ = 'Paper'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_id = db.Column(db.Integer, db.ForeignKey('Source.id'))
    title = db.Column(db.String(128))
    publication_date = db.Column(db.Date)
    pub_type = db.Column(db.String(128))
    content_type = db.Column(db.String(128))
    abstract = db.Column(db.String(1024))
    full_text = db.Column(db.String(1024))
    citation_count = db.Column(db.Integer)
    doi = db.Column(db.String)
    url = db.Column(db.String)

    # Many to one in which paper is child
    # Papers can only be published in one journal at a time
    source = relationship("Source", back_populates="papers")

    # Many to many relationships
    paper_authors = relationship(
        "AuthorWritesPaper",
        backref="paper",
        cascade="save-update, merge, delete, delete-orphan"
    )
    databases = relationship(
        "PaperIsInDB",
        backref="paper",
        cascade="save-update, merge, delete, delete-orphan"
    )
    search_strings = relationship(
        "PaperHasSearchString",
        backref="paper",
        cascade="save-update, merge, delete, delete-orphan"
    )
    tags = relationship(
        'PaperHasTag',
        backref='paper',
        cascade="save-update, merge, delete, delete-orphan"
    )
    un_goals = relationship(
        'PaperHasUNGoal',
        backref='paper',
        cascade="save-update, merge, delete, delete-orphan"
    )
