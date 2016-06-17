from unittest import TestCase

from flask import json

from application import db, app
import views

from tests.test_config import config


class WikiServerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}/{database}'.format(**config)
        app.app_context().push()
        db.init_app(app)

        cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add_page(self, title, text):
        return self.app.post('/page', data=json.dumps(dict(
            title=title,
            text=text
        )), content_type='application/json')

    def test_add_get_pages(self):
        r = self.app.get('/pages')
        self.assertEquals(json.loads(r.get_data()), {})

        r = self.add_page('p1', '1v1')
        d = json.loads(r.get_data())
        p1_id = d['id']

        r = self.app.get('/pages')
        data = r.get_data()
        titles = json.loads(data).values()
        self.assertSetEqual(set(titles), {'p1'})

        r = self.add_page('p1', '2v1')
        self.assertEquals(r.status_code, 409)

        r = self.add_page('p2', '2v1')
        d = json.loads(r.get_data())
        p2_id = d['id']

        r = self.app.get('/pages')
        d = json.loads(r.get_data())
        self.assertEquals(d, {str(p1_id): 'p1', str(p2_id): 'p2'})

    def test_page_version(self):
        r = self.add_page('p1', '1v1')
        d = json.loads(r.get_data())
        p1_id = d['id']

        r = self.app.get('/page/{}'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, version=1, title='p1', text='1v1'))

        r = self.app.get('/page_by_title/p1')
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, version=1, title='p1', text='1v1'))

        r = self.app.get('/page/{}/versions'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(versions=[1]))

        r = self.app.post('/page/{}/version'.format(p1_id), data=json.dumps(dict(
            text='1v2'
        )), content_type='application/json')

        d = json.loads(r.get_data())
        self.assertEquals(d, dict(result='OK'))

        r = self.app.get('/page/{}/versions'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(versions=[1, 2]))

        r = self.app.get('/page/{}/current_version'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, current_version=2))

        r = self.app.get('/page/{}'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, version=2, title='p1', text='1v2'))

        r = self.app.post('/page/{}/current_version'.format(p1_id), data=json.dumps(dict(
            version=3
        )), content_type='application/json')
        self.assertEquals(r.status_code, 404)

        r = self.app.post('/page/{}/current_version'.format(p1_id), data=json.dumps(dict(
            version=1
        )), content_type='application/json')
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(result='OK'))

        r = self.app.get('/page/{}/current_version'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, current_version=1))

        r = self.app.get('/page/{}'.format(p1_id))
        d = json.loads(r.get_data())
        self.assertEquals(d, dict(id=p1_id, version=1, title='p1', text='1v1'))
