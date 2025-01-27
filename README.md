# flask-app-template
This is a template for a basic flask application


## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)



## Features

- Modular structure for Flask applications.
- Integration with SQLAlchemy for database management.
- Simple configuration for development and production environments.
- Database migrations support using Flask-Migrate.
- Ready-to-use HTML templates with Jinja2.
- Prepared for adding routes, models, and views.



## Requirements

Before starting, ensure you have the following installed:

- Python >= 3.10.
- pip
- Virtualenv (optional but recommended for isolated environments).
- Flask >= 3.x
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Compress
- Flask-CORS
- werkzeug
- smtplib
- email



## Installation

Follow these steps to clone and install the application locally:

1. Clone the repository:
   ```
   git clone https://github.com/Daniel-OM/flask-app-template.git
   cd flask-app-template
   ```

2. Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Configure environment variables (create a `.env` file if needed):
    ```
    FLASK_APP=web/app.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    DATABASE_URI=sqlite:///app.db  # Change according to your database
    ```

5. Configure the application settings in (`web/config.py`).

6. Initialize the database (if applicable):
    ```
    flask db init
    flask db migrate
    flask db upgrade
    ```



## Project Structure

```
repository/
│
├── web/                    # Main application code
│   ├── __init__.py         # Package initialization
│   ├── migrations/         # Database migration files
│   ├── backend/            # Backend application files
|   |   ├── __init__.py     # Package initialization
│   │   ├── api/            # API files
│   │   ├── database/       # Database management files
│   │   ├── src/            # External application code
│   │   ├── login.py        # Login module initialization
│   │   └── models.py       # Data models using SQLAlchemy
│   │   
│   ├── frontend/           # Frontend application files
|   |   ├── __init__.py     # Package initialization
│   │   ├── static/         # Static files
│   │   │   ├── css/        # CSS files
│   │   │   └── js/         # JavaScript files
│   │   └── templates/      # HTML templates
│   │   
│   ├── app.py              # Main application entry point
│   ├── config.py           # Environment variables configuration
│   ├── web.ini             # Server configuration
│   └── wsgi.py             # WSGI entry point for subroutes
│
├── tests/                  # Application tests
│   ├── test_routes.py      # Routes testing
│   └── test_models.py      # Models testing
│
├── .env                    # Environment variables (not to be uploaded to GitHub)
├── .gitignore              # Ignore unnecessary files and folders
├── requirements.txt        # Repository dependencies
├── README.md               # Project documentation
└── LICENSE                 # Repository license
```



## Usage

To run the application, activate the virtual environment and use the following command from the `web/` directory:

    flask --app backend.app run --reload

To view the application open your browser and access: http://127.0.0.1:5000



## Testing
To run the tests, use the following command:

    pytest

Tests are located in the `tests/` directory and cover routes, models, etc.



## Deployment
### Production

1. Set up a web server with Gunicorn:
    ```
    pip install gunicorn
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
    ```

2. Configure a reverse proxy like Nginx to forward requests to the Flask server.

3. Adjust environment variables:

    ```
    FLASK_ENV=production
    DATABASE_URI=<your_database_uri>
    ```

### Cloud Services

The project can easily be deployed on platforms like Heroku, AWS, or Render.



## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/nueva-funcionalidad`).
3. Make your changes and push them (`git push origin feature/nueva-funcionalidad`).
4. Create a Pull Request.



## License

This project is licensed under the [Licencia MIT](LICENSE).  
See the `LICENSE` file for more details.