
import enum
import datetime as dt

from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from .config import config, serializer
from .models import db, migrate, Role, User



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
        

class ApiResponse:

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

class APITemplate:
    
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
      
class RoleAPI(APITemplate):

    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)
    
    def get(self) -> ApiResponse:

        try:
            items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                self.db.session.query(Role).filter(Role.active == True).all()]
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Roles obtained.',
                                                data=items)
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, id:int) -> ApiResponse:

        try:
            item: dict = entityToDict(entity=self.db.session.query(Role).filter(Role.id == id).first(), 
                                    hidden_fields=['_sa_instance_state'])

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Role obtained.',
                                                data=item)
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def post(self, name:str, active:bool=True) -> ApiResponse:
        
        try:
            item: Role = Role(
                name = name,
                active = active)
            self.db.session.add(item)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Role registered.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def update(self, id:int, form:dict={}, name:str=None, active:bool=None) -> ApiResponse:
        
        try:
            data: dict = form
            if name != None: data['name'] = name
            if active != None: data['active'] = active
        
            self.db.session.query(Role).filter(Role.id == id).update(data)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Role updated.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def delete(self, id:int, permanent:bool=False) -> ApiResponse:
        
        try:
            if permanent:
                self.db.session.query(Role).filter(Role.id == id).delete()
            else:
                self.db.session.query(Role).filter(Role.id == id).update({'active': False})

            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='Role deleted.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response

class UserAPI(APITemplate):
    
    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)

    def post(self, email:str, password:str, first_name:str, username:str,
            last_name:str=None, role_id:int=2, active:bool=True) -> ApiResponse:
        
        try:
            new_user: User = User(
                username = username,
                name = first_name, 
                surname = last_name if last_name != None else None, 
                email = email, 
                password = generate_password_hash(password=password),
                role_id = role_id,
                active = active
            )
            self.db.session.add(instance=new_user)
            self.commit()
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User registered.',
                                                data=new_user.id)    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def login(self, email:str, password:str) -> ApiResponse:
        
        try:
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            
            if user:
                if check_password_hash(pwhash=user.password, password=password):
                    login_user(user=user, remember=True)
                    response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='User logged.')
                else:
                    response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=False, description='Bad password.')   
            else:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=False, description='No user found.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def logout(self) -> ApiResponse:
        
        try:
            logout_user()
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User logged out.')    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response

    def checkByUser(self, id:int=None, username:str=None, email:str=None) -> ApiResponse:
        
        try:
            exists: dict[str, bool] = {}

            if id != None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.id == id).first(),
                                            hidden_fields=['_sa_instance_state', 'password', 'postal_code', 'max_loss_pct', 
                                                           'birthdate', 'role_id', 'city', 'theme_id', 'type_id', 'surname', 
                                                           'country_id'])
                exists['id'] = entity != None

            if username != None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.username == username).first(),
                                            hidden_fields=['_sa_instance_state', 'password', 'postal_code', 'max_loss_pct', 
                                                           'birthdate', 'role_id', 'city', 'theme_id', 'type_id', 'surname', 
                                                           'country_id'])
                exists['username'] = entity != None

            if email != None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.email == email).first(),
                                            hidden_fields=['_sa_instance_state', 'password', 'postal_code', 'max_loss_pct', 
                                                           'birthdate', 'role_id', 'city', 'theme_id', 'type_id', 'surname', 
                                                           'country_id'])
                exists['email'] = entity != None
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User checked.',
                                                data=exists)
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=None)
        
        return response
    
    def getById(self, id:int=None, email:str=None, username:str=None, 
                unwanted_keys:list=['_sa_instance_state']) -> ApiResponse:
        
        try:
            if username != None:
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.username == username) \
                                        .join(Role, Role.id == User.role_id).first()
            elif email != None:
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.email == email) \
                                        .join(Role, Role.id == User.role_id).first()
            else:
                id: int = current_user.id if id == None else id
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.id == id) \
                                        .join(Role, Role.id == User.role_id).first()
            
            user: dict = {**entityToDict(entity=entity[0],hidden_fields=unwanted_keys),
                          **{'role': entityToDict(entity=entity[1],hidden_fields=unwanted_keys)}}
            
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User details obtained.',
                                                data=user)
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def update(self, form:dict={}, email:str=None, password:str=None, first_name:str=None, 
                last_name:str=None, role_id:int=None, active:bool=None) -> ApiResponse:
        
        try:
            data: dict = form
            if first_name != None: data['name'] = first_name.capitalize()
            if last_name != None: data['surname'] = last_name.capitalize()
            if email != None: data['email'] = email.capitalize()
            if password != None: data['password'] = generate_password_hash(password=password)
            if role_id != None: data['role_id'] = role_id
            if active != None: data['active'] = active

            
            self.db.session.query(User).filter(User.id == current_user.id).update(data)
            self.commit()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description='User updated.',
                                                data=self.getById(id=current_user.id).data)    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be updated. Error:{e}',
                                                data={})
        
        return response
    
    def delete(self, permanent:bool=False) -> ApiResponse:
        
        try:
            if permanent:
                self.db.session.query(User).filter(User.id == current_user.id).delete()
            else:
                self.db.session.query(User).filter(User.id == current_user.id).update({'active': False})
            self.commit()

            self.logout()

            response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=True, description=f"Account deleted.")    
            
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be deleted. Error:{e}')

        return response
    
    def forgotPassword(self, email:str) -> ApiResponse:
        
        try:
            # user: User = User.query.filter_by(email=email.lower()).first()
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            if user:
                token: str | bytes = serializer.dumps(obj=user.email, salt='reset-password')
                reset_link: str = url_for(endpoint='user_views.reset_password', token=token)

                # TODO: Whould send an email

                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Email sent with the password reset link.')  
            else:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=False, description='There is no user with that email.')
        except Exception as e:
            response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                executed=False, description=e)
            
        return response
    
    def resetPassword(self, token:str=None, password:str=None) -> ApiResponse:

        try:
            if token != None:
                email = serializer.loads(s=token, salt='reset-password', max_age=3600)  # Token válido durante 1 hora
            elif current_user.is_authenticated:
                email = current_user.email
        except:
            return ApiResponse(status=ApiResponse.Status.SUCCESS, 
                            executed=False, description='The reset link is not valid or has expired.')  
            
        if password != None:
            try:
                self.db.session.query(User).filter(User.email == email).update({
                    'password': generate_password_hash(password=password)
                })
                self.commit()
                
                response: ApiResponse =  ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                    executed=True, description='Password changed.')
            
            except Exception as e:
                response: ApiResponse = ApiResponse(status=ApiResponse.Status.ERROR, 
                                                    executed=False, description=f'Error changing the password. Try again. ({e})')

        else:
            response: ApiResponse =  ApiResponse(status=ApiResponse.Status.SUCCESS, 
                                                executed=False, description=False)  
        
        return response
