from sqlalchemy import Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship

from application import db


class WikiPage(db.Model):
    __tablename__ = 'wikipage'

    id = Column(Integer, primary_key=True)

    title = Column(String, index=True, unique=True, nullable=False)
    current_version_id = Column(Integer,
                                ForeignKey('wikipageversion.id', name='kf_current_version', ondelete='SET NULL'))
    current_version = relationship('WikiPageVersion', foreign_keys=current_version_id)


class WikiPageVersion(db.Model):
    __tablename__ = 'wikipageversion'
    __table_args__ = (
        Index('page_version_index', 'wikipage_id', 'number', unique=True),
    )

    id = Column(Integer, primary_key=True)

    wikipage_id = Column(Integer, ForeignKey('wikipage.id'), nullable=False)
    wikipage = relationship('WikiPage', foreign_keys=wikipage_id, backref='versions')

    number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
