
from flask import Flask
from flask_admin import Admin

from .views import main_views, user_views
from .login import login_manager
from .config import config
from .models import db, migrate, Role, User
# from flask_admin.contrib.sqla import ModelView
from .adminviews import RoleAdmin, UserAdmin

# Create App
application: Flask = Flask(import_name=__name__, instance_relative_config=True)
application.config.from_mapping(mapping=config)

application.jinja_env.auto_reload = True

application.register_blueprint(blueprint=main_views, url_prefix='/')
application.register_blueprint(blueprint=user_views, url_prefix='/user')


login_manager.init_app(app=application)
db.init_app(app=application)
migrate.init_app(app=application, db=db)

# with application.app_context():
#     db.create_all()
#     db.session.commit()

admin: Admin = Admin(app=application, name='Admin Panel', template_mode='bootstrap4')
# Register the models with Flask-Admin
admin.add_view(view=RoleAdmin(model=Role, session=db.session))
admin.add_view(view=UserAdmin(model=User, session=db.session))


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
