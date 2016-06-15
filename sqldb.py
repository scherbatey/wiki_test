import json

from sqlalchemy import create_engine, Text, Index
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import relationship

from sqldb_config import config

import logging
logger = logging.getLogger(__name__)

engine = create_engine('postgresql://{user}:{password}@{host}/{database}'.format(**config),
                       echo=False)
Session = scoped_session(sessionmaker(bind=engine,
                                      autocommit=False,
                                      autoflush=False))


def _commit_model(model, raise_exception=False):
    Session.add(model)
    try:
        Session.commit()
    except Exception as e:
        logger.error("Error: ", e)
        Session.rollback()
        if raise_exception:
            raise
        return False
    return True

Base = declarative_base()
Base.query = Session.query_property()
Base.commit = _commit_model


def init_db():
    Base.metadata.create_all(bind=engine)


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
