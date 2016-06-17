from flask import Flask, jsonify, abort, request, json, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from application import app, db
from models import WikiPage, WikiPageVersion

import logging
logger = logging.getLogger(__name__)


@app.route('/pages')
def get_all_pages():
    pages = db.session.query(WikiPage).all()
    result = {p.id: p.title for p in pages}
    return jsonify(result)
    # return Response(json.dumps(result), content_type='application/json')


@app.route('/page', methods=['POST'])
def create_new_page():
    data = request.get_json(silent=True)
    if data is None:
        abort(400)
    try:
        page = WikiPage(title=data['title'])
        page_version = WikiPageVersion(wikipage=page, number=1, text=data['text'])
        # FIXME: do it in one commit somehow
        db.session.add(page)
        db.session.commit()
        page.current_version = page_version
        db.session.commit()
    except KeyError:
        abort(400)
    except IntegrityError:
        db.session.rollback()
        abort(409)

    return jsonify(result='OK', id=page.id)


@app.route('/page/<int:id>', defaults={'title': None})
@app.route('/page_by_title/<string:title>', defaults={'id': None})
def get_page_current_version(id, title):
    try:
        page_query = db.session.query(WikiPage).options(joinedload(WikiPage.current_version))
        if id is not None:
            page = page_query.filter_by(id=id).one()
        else:
            page = page_query.filter_by(title=title).one()
    except NoResultFound:
        abort(404)
    return jsonify(id=page.id, title=page.title, text=page.current_version.text, version=page.current_version.number)


@app.route('/page/<int:id>/versions')
def get_page_versions(id):
    try:
        page_versions = db.session.query(WikiPageVersion).filter_by(
            wikipage_id=id,
        ).all()
    except NoResultFound as e:
        abort(404)
    return jsonify(versions=[v.number for v in page_versions])


@app.route('/page/<int:id>/current_version')
def get_page_current_version_id(id):
    try:
        page = db.session.query(WikiPage).filter_by(id=id).one()
    except NoResultFound:
        abort(404)
    return jsonify(id=page.id, current_version=page.current_version_id)


@app.route('/page/<int:id>/current_version', methods=['POST'])
def set_page_current_version(id):
    data = request.get_json(silent=True)
    if data is None:
        abort(400)
    try:
        page_version = db.session.query(WikiPageVersion).options(joinedload(WikiPageVersion.wikipage)).filter_by(
            wikipage_id=id,
            number=data['version']
        ).one()
        page_version.wikipage.current_version = page_version
        db.session.commit()
    except NoResultFound:
        abort(404)
    except KeyError:
        abort(400)
    return jsonify(result='OK')


@app.route('/page/<int:id>/version/<int:version>')
def get_page_version(id, version):
    try:
        page_version = db.session.query(WikiPageVersion).options(joinedload(WikiPageVersion.wikipage)).filter_by(
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
        abort(400)
    try:
        new_version_number = (
            db.session.query(func.max(WikiPageVersion.number))
                .group_by(WikiPageVersion.wikipage_id)
                .filter_by(wikipage_id=id).one()
        )[0] + 1
        new_page_version = WikiPageVersion(wikipage_id=id, text=data['text'], number=new_version_number)
        page = db.session.query(WikiPage).filter_by(id=id).one()
        page.current_version = new_page_version
        db.session.add(new_page_version)
        db.session.commit()
        return jsonify(result='OK')
    except NoResultFound:
        abort(404)


