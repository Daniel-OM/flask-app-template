
from flask import Flask
from flask_admin import Admin
from flask_compress import Compress
from flask_cors import CORS

from .config import config
from .backend.login import login_manager
from .backend.models import db, migrate
from .backend.api.pages import pages_api
from .backend.api.user import user_api
from .backend.api.role import role_api

# flask --app backend.app run --reload

# Create App
application: Flask = Flask(import_name=__name__, instance_relative_config=True)
application.config.from_mapping(mapping=config)

application.jinja_env.auto_reload = True

application.register_blueprint(blueprint=pages_api, url_prefix='/')
application.register_blueprint(blueprint=user_api, url_prefix='/api/user')
application.register_blueprint(blueprint=role_api, url_prefix='/api/role')


login_manager.init_app(app=application)
db.init_app(app=application)
migrate.init_app(app=application, db=db)
compress = Compress()
compress.init_app(app=application)
cors = CORS()
cors.init_app(app=application, supports_credentials=True)

# with application.app_context():
#     db.create_all()
#     db.session.commit()


if __name__ == '__main__':

    # Print SQL in command window
    db.engine.echo = True
    application.config['SQLALCHEMY_ECHO'] = True

    application.run(port=5001, debug=True)


    '''
    To create the database you must open the flask shell in the terminal:
    >> flask shell

    And execute the initialization
    >> app.app_context().push()

    >> from app import db, Role, User
    >> db.create_all()

    The db.create_all() function does not recreate or update a table if it 
    already exists. For example, if you modify your model by adding a new column, 
    and run the db.create_all() function, the change you make to the model will 
    not be applied to the table if the table already exists in the database. The 
    solution is to delete all existing database tables with the db.drop_all() 
    function and then recreate them with the db.create_all() function like so:
    >> db.drop_all()
    >> db.create_all()

    Sin estar en la shell de flask:
    
    To create migration file:
    >> flask db init

    To make a migration:
    >> flask db migrate -m "Initial migration."
    >> flask db upgrade 
    '''
