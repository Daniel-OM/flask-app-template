import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Asegurarse de que el directorio raíz está en sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Cargar variables de entorno
load_dotenv()

# Crear el directorio 'instance' si no existe
instance_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(name='instance', exist_ok=True)

# Crear aplicación Flask con la configuración adecuada
from app import create_app, db

env: str = os.environ.get('FLASK_ENV', default='development')
app: Flask = create_app(config_name=env)

# Inicializar Flask-Migrate
migrate = Migrate(app=app, db=db)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Crear todas las tablas en la base de datos
            db.create_all()
            print("Tablas creadas correctamente.")
        except Exception as e:
            # Manejar errores al crear las tablas
            print(f"Error al crear las tablas: {e}")
            print(f"Ruta de la base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Iniciar el servidor Flask
    app.run(host='0.0.0.0', port=5000)