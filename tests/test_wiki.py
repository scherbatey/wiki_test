from unittest import TestCase

import views
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from application import db, app
from tests.test_config import config


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

        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}/{database}'.format(**config)
        app.app_context().push()
        db.init_app(app)


    @classmethod
    def tearDownClass(cls):
        pass
        # cls.admin_session.execute("drop database {database}".format(**config))

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_get_pages(self):
        test_app = app.test_client()
        r = test_app.get('/pages')
        print(r)
