from flask import Flask, jsonify, abort
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from sqldb import WikiPage, WikiPageVersion

app = Flask(__name__)


@app.route('/page/<int:id>')
def get_page(id):
    try:
        page = WikiPage.query.options(joinedload(WikiPage.current_version)).get(id)
    except NoResultFound as e:
        abort(404)
    return jsonify(title=page.title, text=page.current_version.text)


@app.route('/page/<int:id>/version/<int:version>')
def get_page_version(id, version):
    try:
        page_version = WikiPageVersion.query.options(joinedload(WikiPageVersion.wikipage)).filter_by(
            wikipage_id=id,
            number=version
        ).one()
    except NoResultFound as e:
        abort(404)
    return jsonify(title=page_version.wikipage.title, text=page_version.text)


if __name__ == '__main__':
    app.run(port=8888)
