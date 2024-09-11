
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

from .config import config


db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

class Role(db.Model):
    __tablename__: str = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
    
class User(db.Model, UserMixin):
    __tablename__: str = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    surname = db.Column(db.String(250), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id), nullable=False)
    role_fk = db.relationship(Role, backref=db.backref('user_role_fk', lazy=True))
    created_at = db.Column(db.Date, default=dt.datetime.now(dt.timezone.utc) if 'sqlite' in config['SQLALCHEMY_DATABASE_URI'] \
                                else dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%Z'), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<User {self.email} ({self.name})>'
