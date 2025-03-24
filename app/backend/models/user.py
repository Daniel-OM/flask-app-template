
import datetime as dt
from flask_login import UserMixin

from app import db, bcrypt
from ..utils.models_utils import checkNone
from .role import Role

class User(db.Model, UserMixin):
    __tablename__: str = 'users' # Table name definition
    
    # Properties definition
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), unique=False, nullable=False)
    last_name = db.Column(db.String(250), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id), nullable=False)
    role_fk = db.relationship(Role, backref=db.backref('Role.id', lazy=True))
    created_at = db.Column(db.Date, default=dt.datetime.now(dt.timezone.utc), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f'<User {self.email} ({self.name})>'

    def __init__(self, email, password, username, first_name, last_name):
        self.email = email
        self.password = password  # Esto usará la property setter
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    @property
    def password(self):
        """Prevenir lectura de contraseña"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Hashear contraseña"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        """Verificar contraseña"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
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
