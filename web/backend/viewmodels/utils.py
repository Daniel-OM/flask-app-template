
import enum
import datetime as dt

from flask_sqlalchemy import SQLAlchemy


def formatDict(dic:dict) -> dict:
    
    for k, v in dic.items():
        if isinstance(v, dict):
            dic[k] = formatDict(dic=v)
        elif v == None:
            continue
        elif isinstance(v, dt.date) or isinstance(v, dt.datetime):
            dic[k] = v.strftime(format='%Y-%m-%d %H:%M')
        elif not isinstance(v, str) and not isinstance(v, float) and not isinstance(v, int):
            dic[k] = float(v)
        else:
            continue
            
    return dic

# entityToDict = lambda entity, hidden_fields: {k: v for k, v in entity.__dict__.items() if k not in hidden_fields}
def entityToDict(entity, hidden_fields:list=[]) -> (None | dict):
    return formatDict(dic={k: v for k, v in entity.__dict__.items() if k not in hidden_fields}) \
        if entity != None else None
        

class ViewModelResponse:

    class Status(enum.Enum):
        SUCCESS: str = 'success'
        ERROR: str = 'error'

    def __init__(self, status:Status=Status.SUCCESS, executed:bool=True, description:str='',
                 data:(list | dict)= None) -> None:
        self.status: self.Status = status
        self.executed: bool = executed
        self.description: str = description
        self.data: list | dict = data

    def to_dict(self) -> dict:
        return {
            'status': self.status.value,
            'executed': self.executed,
            'description': self.description,
            'data': self.data
        }

class ViewModelTemplate:
    
    def __init__(self, db:SQLAlchemy) -> None:
        self.db: SQLAlchemy = db
    
    def formToDict(self, form) -> dict:
        
        '''
        form: ImmutableMultiDict
        '''
        
        return {k: v[0] if len(v) == 1 else v
                for k, v in form.to_dict(flat=False).items() \
                if v or v > 0 or len(v) > 0}
        
    def commit(self) -> None:
        self.db.session.commit()