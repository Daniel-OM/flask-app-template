
import os
from itsdangerous import URLSafeTimedSerializer

basedir: str = os.path.abspath(path=os.path.dirname(p=__file__))

config: dict[str, (str | bool)] = {
    'SECRET_KEY': 'dev-application',
    'TEMPLATES_AUTO_RELOAD': True,
    'SQLALCHEMY_DATABASE_URI': '<DATABASE_STRING>',
}

# Configuración del serializer para generar tokens seguros
serializer = URLSafeTimedSerializer(secret_key=config['SECRET_KEY'])

date_format = '%Y-%m-%d %H:%M:%S.%f%z'

email_config: dict[str, str] = {
    'email': '<EMAIL>', 
    'password': '<PASSWORD>'
}

from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-muy-segura'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB límite para uploads
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-clave-secreta'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    # Usar una ruta absoluta para la base de datos
    # En config.py, clase DevelopmentConfig
    SQLALCHEMY_DATABASE_URI = 'sqlite:///repairconnect.db'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # Tiempo largo para facilitar desarrollo


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test.db'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuración para producción"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Añadir configuraciones de seguridad para producción
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


# Diccionario para seleccionar configuración según entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}