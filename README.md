# flask-app-template
This is a template for a basic flask application

---

## Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Pruebas](#pruebas)
- [Despliegue](#despliegue)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)



## Características

- Estructura modular para aplicaciones Flask.
- Integración con SQLAlchemy para la gestión de bases de datos.
- Configuración sencilla para entornos de desarrollo y producción.
- Soporte para migraciones de bases de datos con Flask-Migrate.
- Plantillas HTML listas para personalización con Jinja2.
- Listo para añadir rutas, modelos y vistas.



## Requisitos

Antes de empezar, asegúrate de tener instalados los siguientes elementos:

- Python >= 3.10.
- pip
- Virtualenv (opcional, recomendado para entornos aislados).
- Flask >= 2.x
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Compress
- Flask-CORS
- werkzeug
- smtplib
- email



## Instalación

Sigue estos pasos para clonar e instalar la aplicación en tu entorno local:

1. Clonar el repositorio:
   ```
   git clone https://github.com/Daniel-OM/flask-app-template.git
   cd flask-app-template
   ```

2. Crear y activar un entorno virtual:
    ```
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Instalar las dependencias
    ```
    pip install -r requirements.txt
    ```

4. Configurar las variables de entorno (crea un archivo `.env` si es necesario):
    ```
    FLASK_APP=web/app.py
    FLASK_ENV=development
    SECRET_KEY=tu_clave_secreta
    DATABASE_URI=sqlite:///app.db  # Cambiar según el sistema de base de datos
    ```

5. Configurar el archivo de configuración de la aplicación (`web/config.py`).

6. Inicializar la base de datos (si aplica):
    ```
    flask db init
    flask db migrate
    flask db upgrade
    ```



## Estructura del proyecto

```
repository/
│
├── web/                    # Código principal de la aplicación
│   ├── __init__.py         # Inicialización del paquete
│   ├── migrations/         # Archivos de migraciones de la base de datos
│   ├── backend/            # Archivos del backend de la aplicación
|   |   ├── __init__.py     # Inicialización del paquete
│   │   ├── api/            # Archivos de la api
│   │   ├── database/       # Archivos de gestores de la base de datos
│   │   ├── src/            # Código externo a la aplicación
│   │   ├── login.py        # Incialización del módulo de login
│   │   └── models.py       # Modelos de datos con SQLAlchemy
│   │   
│   ├── frontend/           # Archivos del frontend de la aplicación
|   |   ├── __init__.py     # Inicialización del paquete
│   │   ├── static/         # Archivos de la api
│   │   │   ├── css/        # Archivos CSS
│   │   │   └── js/         # Archivos JavaScript
│   │   └── templates/      # Archivos de gestores de la base de datos
│   │   
│   ├── app.py              # Archivo principal de la aplicación
│   ├── config.py           # Configuración para variables de entorno
│   ├── web.ini             # Servidor
│   └── wsgi.py             # Para subrutas
│
├── tests/                  # Tests para la aplicación
│   ├── test_routes.py      # Pruebas de rutas
│   └── test_models.py      # Pruebas de modelos
│
├── .env                    # Variables de entorno (no subir a GitHub)
├── .gitignore              # Ignorar archivos y carpetas innecesarias
├── requirements.txt        # Dependencias del repositorio
├── README.md               # Documentación del proyecto
└── LICENSE                 # Licencia del repositorio
```



## Uso

Para ejecutar la aplicación, activa el entorno y usa el siguiente comando desde la carpeta `web/`:

    flask --app backend.app run --reload

Para ver la aplicación abre tu navegador y accede a http://127.0.0.1:5000



## Pruebas
Para ejecutar las pruebas, usa el comando:

    pytest

Las pruebas están en el directorio `tests/` y cubren (rutas, modelos, etc.).



## Despliegue
### Producción

1. Configura un servidor web como Gunicorn:
    ```
    pip install gunicorn
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
    ```

2. Configura un proxy inverso como Nginx para redirigir las solicitudes al servidor Flask.

3. Ajusta las variables de entorno:

    ```
    FLASK_ENV=production
    DATABASE_URI=<URI_de_tu_base_de_datos>
    ```

### Servicios en la nube

El proyecto puede ser desplegado fácilmente en plataformas como Heroku, AWS, o Render.



## Contribuciones

Las contribuciones son bienvenidas. Sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz tus cambios y súbelos (`git push origin feature/nueva-funcionalidad`).
4. Crea un Pull Request.



## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).  
Consulta el archivo `LICENSE` para más detalles.