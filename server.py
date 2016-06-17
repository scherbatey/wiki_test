import views
import models

from application import app, db
from config import config

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}/{database}'.format(**config)

db.init_app(app)

if __name__ == '__main__':
    app.run(port=8888)

