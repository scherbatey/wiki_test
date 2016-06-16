from sqlalchemy import create_engine, Text, Index
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import relationship


def init_db(engine):
    Base.metadata.create_all(bind=engine)

Base = declarative_base()


class WikiPage(Base):
    __tablename__ = 'wikipage'

    id = Column(Integer, primary_key=True)

    title = Column(String, index=True, unique=True, nullable=False)
    current_version_id = Column(Integer, ForeignKey('wikipageversion.id'))
    current_version = relationship('WikiPageVersion', foreign_keys=current_version_id)


class WikiPageVersion(Base):
    __tablename__ = 'wikipageversion'
    __table_args__ = (
        Index('page_version_index', 'wikipage_id', 'number', unique=True),
    )

    id = Column(Integer, primary_key=True)

    wikipage_id = Column(Integer, ForeignKey('wikipage.id'), nullable=False)
    wikipage = relationship('WikiPage', foreign_keys=wikipage_id, backref='versions')

    number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
