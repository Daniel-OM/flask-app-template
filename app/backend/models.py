
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

from ..config import config, date_format

def checkNone(value, format): return format(value) if value is not None else None
def checkNoneDate(value): return value.strftime(format=date_format) if value is not None else None


db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

class Role(db.Model):
    __tablename__: str = 'roles' # Table name definition
    
    # Properties definition
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

    def to_dict(self, unwanted_keys:list[str]|None=None) -> dict:
        return {k:v for k, v in {
            'id': checkNone(value=self.id, format=int),
            'name': checkNone(value=self.name, format=str),
            'active': self.active
        }.items() if unwanted_keys == None or k not in unwanted_keys}
    
class User(db.Model, UserMixin):
    __tablename__: str = 'users' # Table name definition
    
    # Properties definition
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    surname = db.Column(db.String(250), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id), nullable=False)
    role_fk = db.relationship(Role, backref=db.backref('user_role_fk', lazy=True))
    created_at = db.Column(db.Date, default=dt.datetime.now(dt.timezone.utc) if 'sqlite' in config['SQLALCHEMY_DATABASE_URI'] \
                                else dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%Z'), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<User {self.email} ({self.name})>'

    def to_dict(self, unwanted_keys:list[str]|None=['passwrod']) -> dict:
        return {k:v for k, v in {
            'id': checkNone(value=self.id, format=int),
            'username': checkNone(value=self.username, format=str),
            'name': checkNone(value=self.name, format=str),
            'surname': checkNone(value=self.surname, format=str),
            'email': checkNone(value=self.email, format=str),
            'password': checkNone(value=self.password, format=str),
            'verified': checkNone(value=self.verified, format=bool),
            'role_id': checkNone(value=self.role_id, format=int),
            'created_at': checkNone(value=self.created_at, format=str),
            'active': self.active
        }.items() if unwanted_keys == None or k not in unwanted_keys}
