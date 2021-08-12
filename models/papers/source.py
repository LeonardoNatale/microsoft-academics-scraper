from models.base import Base
from models.base_table import BaseTable
import sqlalchemy as db
from sqlalchemy.orm import relationship

# One to many with paper (a paper can only be published in one journal)
class Source(Base, BaseTable):
    __tablename__ = 'Source'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    # Many to one relationship in which source is the parent
    papers = relationship("Paper", back_populates="source")