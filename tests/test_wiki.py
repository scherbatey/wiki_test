import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from unittest import TestCase

import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import scoped_session, sessionmaker

from sqldb import init_db, Base
from tests.test_config import config

from server import app, engine

executor = ThreadPoolExecutor()

class WikiServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        admin_engine = create_engine("postgres://{admin}:{admin_password}@{host}/{admin_database}".format(**config))
        cls.admin_session = sessionmaker(bind=admin_engine)()
        cls.admin_session.connection().connection.set_isolation_level(0)
        try:
            cls.admin_session.execute("drop database {database}".format(**config))
        except ProgrammingError:
            pass
        cls.admin_session.execute("create database {database} owner {user}".format(**config))

        cls.session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

        Base.metadata.create_all(bind=engine)

        executor.submit(app.run, port=9999)

    @classmethod
    def tearDownClass(cls):
        executor.shutdown()

    def tearDown(self):
        self.session.execute("truncate table wikipage cascade")

    def test_get_pages(self):
        r = requests.get('127.0.0.1:9999/pages')
        print(r)
