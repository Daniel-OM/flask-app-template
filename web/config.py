
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