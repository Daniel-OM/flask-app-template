import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager  # Se usa Flask-Login para que current_user esté disponible en los templates

from .config import config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

# Inicializar LoginManager
login_manager = LoginManager()

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask orientada a un SPA con JWT y Flask-Login para renderizado condicional"""
    app = Flask(import_name=__name__, instance_relative_config=True,
                static_folder='frontend/static', 
                # static_url_path='/flask_static',
                template_folder='frontend/html')
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Asegurar que existe el directorio instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    
    # Inicializar LoginManager con la app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ruta de login, si se requiere redirección
    
    # Definir user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.backend.models import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints (rutas de la API)
    from .backend.routes import (pages_bp, role_bp, user_bp, docs_bp)
    app.register_blueprint(errorlog_bp, url_prefix='/api/error-log')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(landing_bp, url_prefix='/')
    app.register_blueprint(docs_bp, url_prefix='/api/docs')

    return app
