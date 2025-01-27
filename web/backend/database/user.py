
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from ...config import config, serializer, email_config
from ...backend.models import User, Role
from .utils import ManagerTemplate, DBResponse, entityToDict
from ...backend.src.email_send import EmailSender

class UserManager(ManagerTemplate):
    
    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)

    def get(self, unwanted_keys:list=['_sa_instance_state']) -> DBResponse:
        
        try:
            entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                    .filter(User.active) \
                                    .join(Role, Role.id == User.role_id).all()
            
            user: dict = {**entityToDict(entity=entity[0],hidden_fields=unwanted_keys),
                          **{'role': entityToDict(entity=entity[1],hidden_fields=unwanted_keys)}}
            
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Users obtained.',
                                                data=user)
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def post(self, email:str, password:str, first_name:str, username:str,
            last_name:str=None, role_id:int=2, active:bool=True) -> DBResponse:
        
        try:
            new_user: User = User(
                username = username,
                name = first_name, 
                surname = last_name if last_name is not None else None, 
                email = email, 
                password = generate_password_hash(password=password),
                role_id = role_id,
                active = active
            )
            self.db.session.add(instance=new_user)
            self.commit()
            
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User registered.',
                                                data=new_user.id)    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def login(self, email:str, password:str) -> DBResponse:
        
        try:
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            
            if user:
                if check_password_hash(pwhash=user.password, password=password):
                    login_user(user=user, remember=True)
                    response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                    executed=True, description='User logged.')
                else:
                    response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                    executed=False, description='Bad password.')   
            else:
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=False, description='No user found.')    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def logout(self) -> DBResponse:
        
        try:
            logout_user()
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User logged out.')    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response

    def checkByUser(self, id:int=None, username:str=None, email:str=None) -> DBResponse:
        
        try:
            exists: dict[str, bool] = {}

            if id is not None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.id == id).first(),
                                            hidden_fields=['_sa_instance_state', 'password'])
                exists['id'] = entity is not None

            if username is not None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.username == username).first(),
                                            hidden_fields=['_sa_instance_state', 'password'])
                exists['username'] = entity is not None

            if email is not None:
                entity: dict = entityToDict(entity=self.db.session.query(User).filter(User.email == email).first(),
                                            hidden_fields=['_sa_instance_state', 'password'])
                exists['email'] = entity is not None
            
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User checked.',
                                                data=exists)
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=None)
        
        return response
    
    def getById(self, id:int=None, email:str=None, username:str=None, 
                unwanted_keys:list=['_sa_instance_state']) -> DBResponse:
        
        try:
            if username is not None:
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.username == username) \
                                        .join(Role, Role.id == User.role_id).first()
            elif email is not None:
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.email == email) \
                                        .join(Role, Role.id == User.role_id).first()
            else:
                id: int = current_user.id if id is None else id
                entity: tuple[User, Role] = self.db.session.query(User, Role) \
                                        .filter(User.id == id) \
                                        .join(Role, Role.id == User.role_id).first()
            
            user: dict = {**entityToDict(entity=entity[0],hidden_fields=unwanted_keys),
                          **{'role': entityToDict(entity=entity[1],hidden_fields=unwanted_keys)}}
            
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User details obtained.',
                                                data=user)
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def update(self, form:dict={}, id:int|None=None, email:str=None, password:str=None, name:str=None, 
                surname:str=None, role_id:int=None, active:bool=None) -> DBResponse:
        
        try:
            data: dict = form
            if name is not None: data['name'] = name.capitalize()
            if surname is not None: data['surname'] = surname.capitalize()
            if email is not None: data['email'] = email.capitalize()
            if password is not None: data['password'] = generate_password_hash(password=password)
            if role_id is not None: data['role_id'] = role_id
            if active is not None: data['active'] = active

            
            self.db.session.query(User).filter(User.id == current_user.id if id is None else id).update(data)
            self.commit()

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User updated.',
                                                data=self.getById(id=current_user.id).data)    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be updated. Error:{e}',
                                                data={})
        
        return response
    
    def delete(self, id:int|None=None, permanent:bool=False) -> DBResponse:
        
        try:
            id = current_user.id if id is None else id
            if permanent:
                self.db.session.query(User).filter(User.id == current_user.id).delete()
            else:
                self.db.session.query(User).filter(User.id == current_user.id).update({'active': False})
            self.commit()

            self.logout()

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description=f"Account deleted.")    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=f'Your account couldn\'t be deleted. Error:{e}')

        return response
    
    def forgotPassword(self, email:str) -> DBResponse:
        
        try:
            # user: User = User.query.filter_by(email=email.lower()).first()
            user: User = self.db.session.query(User).filter(User.email == email.lower()).first()
            if user:
                token: str | bytes = serializer.dumps(obj=user.email, salt='reset-password')
                reset_link: str = url_for(endpoint='user_views.reset_password', token=token)

                sender = EmailSender()
                sender.login(user=email_config['email'], password=email_config['password'])
                sender.send(message=f'Click the link to reset the password: {request.root_url}{reset_link}', 
                        subject='Omika Reset password', destinatary=[user.email], files=[])
                sender.logout()
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                    executed=True, description='Email sent with the password reset link.')  
            else:
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                    executed=False, description='There is no user with that email.')
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=str(e))
            
        return response
    
    def resetPassword(self, token:str=None, password:str=None) -> DBResponse:

        try:
            if token is not None:
                email = serializer.loads(s=token, salt='reset-password', max_age=3600)  # Token válido durante 1 hora
            elif current_user.is_authenticated:
                email = current_user.email
        except:
            return DBResponse(status=DBResponse.Status.SUCCESS, 
                            executed=False, description='The reset link is not valid or has expired.')  
            
        if password is not None:
            try:
                self.db.session.query(User).filter(User.email == email).update({
                    'password': generate_password_hash(password=password)
                })
                self.commit()
                
                response: DBResponse =  DBResponse(status=DBResponse.Status.SUCCESS, 
                                                    executed=True, description='Password changed.')
            
            except Exception as e:
                response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                    executed=False, description=f'Error changing the password. Try again. ({e})')

        else:
            response: DBResponse =  DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=False, description=False)  
        
        return response
    
    def verify(self, token:str, commit:bool=True) -> DBResponse:

        try:
            email = serializer.loads(s=token, salt='verify-email', max_age=3600)  # Token válido durante 1 hora

            try:
                self.db.session.query(User).filter(User.email == email) \
                        .update(values={'verified': True if 'postgresql' in config['SQLALCHEMY_DATABASE_URI'] else 1})
                if commit: self.commit()
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                            executed=True, description='User verified.')    
            except Exception as e:
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=False, description=str(e))    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=str(e))

        return response

    def isVerified(self, email:str) -> DBResponse:

        try:
            user: User = self.db.session.query(User).filter(User.email == email).first()
            if user is None:
                response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                            executed=False, description='User not registered.', data=False)
            else:
                if user.verified:
                    response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='User verified.', data=True)    
                else:
                    response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=False, description='User not verified.', data=False)    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=str(e))

        return response
            
