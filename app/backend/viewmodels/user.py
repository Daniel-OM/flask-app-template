
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

from app import db
from . import APIResponse
from ..models import User
from ..utils.api_logger import logger
from ..src.email_send import EmailSender
from ...config import config, serializer, email_config

class UserViewModel:
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def get(details: bool = False, filters:dict[str, (str|int|float|bool)] = None, page:int=1, per_page:int=None) -> APIResponse:
        """
        Obtiene todos los Users con opción de filtrado y paginación
        
        Args:
            details: Si es True, carga las relaciones
            filters: Diccionario con filtros a aplicar {campo: valor}
            page: Número de la página
            per_page: Número de elementos por página
            
        Returns:
            Lista de objetos User
        """
        
        query = User.query
        
        # Aplicar carga de relaciones si se solicita
        if details:
            query.options(joinedload(User.role_fk))

        # Aplicar filtros si existen
        if filters:
            for field, value in filters.items():
                if hasattr(User, field):
                    query = query.filter(getattr(User, field) == value)

        return APIResponse(executed=True, description='Users obtained', data=query.all()) if per_page is None else \
            APIResponse(executed=True, description='Users obtained', data=query.paginate(page=page, per_page=per_page, error_out=False).items)

    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def getById(id:int=None, email:str=None, username:str=None, details: bool = False) -> APIResponse:
        
        query = User.query
        
        if username is not None:
            query = query.filter(User.username == username)
        elif email is not None:
           query = query.filter(User.email == email)
        else:
            id: int = current_user.id if id is None else id
            query = query.filter(User.id == id)
            
        if details:
            query.options(joinedload(User.role_fk))
            
        return APIResponse(executed=True, description='User details obtained.',
                                            data=query.get(id))
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def post(email:str, password:str, first_name:str, username:str,
            last_name:str=None, role_id:int=2, active:bool=True) -> APIResponse:
    
        entity: User = User(
            username = username,
            name = first_name, 
            surname = last_name if last_name is not None else None, 
            email = email, 
            password = password,
            role_id = role_id,
            active = active
        )
        
        db.session.add(entity)
        db.session.commit()
        
        return APIResponse(executed=True, description='User registered.', data=entity.id)
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def login(email:str, password:str) -> APIResponse:
        
        try:
            user: User = User.query.filter(User.email == email.lower()).first()
            
            if user:
                if check_password_hash(pwhash=user.password, password=password):
                    login_user(user=user, remember=True)
                    response: APIResponse = APIResponse(executed=True, description='User logged.')
                else:
                    response: APIResponse = APIResponse(executed=False, description='Bad password.')   
            else:
                response: APIResponse = APIResponse(executed=False, description='No user found.')    
            
        except Exception as e:
            response: APIResponse = APIResponse(executed=False, description=e)
        
        return response
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def logout() -> APIResponse:
        
        try:
            logout_user()
            response: APIResponse = APIResponse(executed=True, description='User logged out.')    
            
        except Exception as e:
            response: APIResponse = APIResponse(executed=False, description=e)
        
        return response

    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def checkByUser(id:int=None, username:str=None, email:str=None) -> APIResponse:
        
        exists: dict[str, bool] = {}
        query = User.query
        if username is not None:
            query = query.filter(User.username == username)
        elif email is not None:
           query = query.filter(User.email == email)
        else:
            id: int = current_user.id if id is None else id
            query = query.filter(User.id == id)
            if id is not None:
                exists['username'] = query.filter(User.id == id).first() is not None

            if username is not None:
                exists['id'] = query.filter(User.username == username).first() is not None

            if email is not None:
                exists['email'] = query.filter(User.email == email).first() is not None
            
        return APIResponse(executed=True, description='User checked.', data=exists)
    

    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def update(id:int, email:str=None, password:str=None, first_name:str=None, 
                last_name:str=None, role_id:int=None, active:bool=None) -> APIResponse:
        
        entity = User.query.get(id)
        if not entity:
            return None
        
        if first_name is not None: setattr(entity, 'first_name', first_name.capitalize())
        if last_name is not None: setattr(entity, 'last_name', last_name.capitalize())
        if email is not None: setattr(entity, 'email', email.lower())
        if password is not None: setattr(entity, 'password', password)
        if role_id is not None: setattr(entity, 'role_id', role_id)
        if active is not None: setattr(entity, 'active', active)

            
        db.session.commit()

        return APIResponse(executed=True, description='User updated.', data=entity)
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def delete(id:int|None=None, permanent:bool=False) -> APIResponse:
        
        entity = User.query.get(id)
        if not entity:
            return APIResponse(executed=False, description='User not found', data=None)

        if permanent:
            db.session.delete(entity)
        else:
            entity.is_active = False

        db.session.commit()
        UserViewModel.logout()

        return APIResponse(executed=True, description='User deleted', data=entity)
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def forgotPassword(email:str) -> APIResponse:
        
        try:
            # user: User = User.query.filter_by(email=email.lower()).first()
            user: User = db.session.query(User).filter(User.email == email.lower()).first()
            if user:
                token: str | bytes = serializer.dumps(obj=user.email, salt='reset-password')
                reset_link: str = url_for(endpoint='user_views.reset_password', token=token)

                sender = EmailSender()
                sender.login(user=email_config['email'], password=email_config['password'])
                sender.send(message=f'Click the link to reset the password: {request.root_url}{reset_link}', 
                        subject='Omika Reset password', destinatary=[user.email], files=[])
                sender.logout()
                response: APIResponse = APIResponse(executed=True, description='Email sent with the password reset link.')  
            else:
                response: APIResponse = APIResponse(executed=False, description='There is no user with that email.')
        except Exception as e:
            response: APIResponse = APIResponse(executed=False, description=str(e))
            
        return response
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def resetPassword(token:str=None, password:str=None) -> APIResponse:

        try:
            if token is not None:
                email = serializer.loads(s=token, salt='reset-password', max_age=3600)  # Token válido durante 1 hora
            elif current_user.is_authenticated:
                email = current_user.email
        except:
            return APIResponse(executed=False, description='The reset link is not valid or has expired.')  
            
        if password is not None:
            try:
                entity = db.session.query(User).filter(User.email == email).fist() 
                setattr(entity, 'password', password)
                db.session.commit()
                
                return APIResponse(executed=True, description='Password changed.')
            
            except Exception as e:
                return APIResponse(executed=False, description=f'Error changing the password. Try again. ({e})')

        else:
            return APIResponse(executed=False, description=False)
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def verify(token:str, commit:bool=True) -> APIResponse:

        email = serializer.loads(s=token, salt='verify-email', max_age=3600)  # Token válido durante 1 hora

        db.session.query(User).filter(User.email == email) \
                .update(values={'verified': True if 'postgresql' in config['SQLALCHEMY_DATABASE_URI'] else 1})
        if commit: db.session.commit()

        return APIResponse(executed=True, description='User verified.')


    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def isVerified(email:str) -> APIResponse:

        user: User = db.session.query(User).filter(User.email == email).first()
        if user is None:
            return APIResponse(executed=False, description='User not registered.', data=False)
        else:
            if user.verified:
                return APIResponse(executed=True, description='User verified.', data=True)    
            else:
                return APIResponse(executed=False, description='User not verified.', data=False)    

            
