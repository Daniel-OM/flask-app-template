
from ... import db
from ..utils.models_utils import checkNone

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
    