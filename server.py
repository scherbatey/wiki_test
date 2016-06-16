from flask import Flask, jsonify, abort, request, json
from sqlalchemy import func, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from sqldb import WikiPage, WikiPageVersion

import logging
logger = logging.getLogger(__name__)

from sqldb_config import config

engine = create_engine('postgresql://{user}:{password}@{host}/{database}'.format(**config), echo=False)
Session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

app = Flask(__name__)


@app.route('/pages')
def get_all_pages():
    pages = Session.query(WikiPage).all()
    result = {p.id: p.title for p in pages}
    return json.dumps(result)


@app.route('/page', methods=['POST'])
def create_new_page():
    data = request.get_json(silent=True)
    if data is None:
        abort(401)
    try:
        page = WikiPage(title=data['title'])
        page_version = WikiPageVersion(wikipage=page, number=1, text=data['text'])
        # FIXME: do it in one commit somehow
        Session.add(page_version)
        Session.commit()
        page.current_version = page_version
        Session.commit()
    except KeyError:
        abort(401)
    except IntegrityError:
        abort(409)

    return jsonify(result='OK', wikipage_id=page.id)


@app.route('/page/<int:id>', defaults={'title': None})
@app.route('/page/<string:title>', defaults={'id': None})
def get_page_current_version(id, title):
    try:
        page_query = Session.query(WikiPage).options(joinedload(WikiPage.current_version))
        if id is not None:
            page = page_query.filter_by(id=id).one()
        else:
            page = page_query.filter_by(title=title).one()
    except NoResultFound:
        abort(404)
    return jsonify(id=page.id, title=page.title, text=page.current_version.text)


@app.route('/page/<int:id>/versions')
def get_page_versions(id):
    try:
        page_versions = Session.query(WikiPageVersion).filter_by(
            wikipage_id=id,
        ).all()
    except NoResultFound as e:
        abort(404)
    return jsonify(versions=[v.number for v in page_versions])


@app.route('/page/<int:id>/current_version')
def get_page_current_version_id(id, version):
    try:
        page = Session.query(WikiPage).filter_by(id=id).one()
    except NoResultFound:
        abort(404)
    return jsonify(id=page.id, current_version_id=page.current_version_id)


@app.route('/page/<int:id>/current_version', methods=['POST'])
def set_page_current_version(id, version):
    try:
        page_version = Session.query(WikiPageVersion).options(joinedload(WikiPageVersion.wikipage)).filter_by(
            wikipage_id=id,
            number=version
        ).one()
        page_version.wikipage.current_version = page_version
        Session.commit()
    except NoResultFound:
        abort(404)
    return jsonify(result='OK')


@app.route('/page/<int:id>/version/<int:version>')
def get_page_version(id, version):
    try:
        page_version = Session.query(WikiPageVersion).options(joinedload(WikiPageVersion.wikipage)).filter_by(
            wikipage_id=id,
            number=version
        ).one()
    except NoResultFound:
        abort(404)
    return jsonify(title=page_version.wikipage.title, text=page_version.text)


@app.route('/page/<int:id>/version', methods=['POST'])
def create_page_new_version(id):
    data = request.get_json(silent=True)
    if data is None:
        abort(401)
    try:
        new_version_number = (
            Session.query(func.max(WikiPageVersion.number))
                .group_by(WikiPageVersion.wikipage_id)
                .filter_by(wikipage_id=id).one()
        )[0] + 1
        new_page_version = WikiPageVersion(wikipage_id=id, text=data['text'], number=new_version_number)
        Session.add(new_page_version)
        Session.commit()
        return jsonify(result='OK', version=new_version_number)
    except NoResultFound:
        abort(404)


if __name__ == '__main__':
    app.run(port=8888)
