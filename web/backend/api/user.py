

from flask import Blueprint, request
from flask_login import login_required, current_user

from .utils import logError

from ..models import db, User
from ..database.utils import DBResponse
from ..database.user import UserManager


user_manager: UserManager = UserManager(db=db)

user_api = Blueprint(name='user_api', import_name=__name__)

@user_api.route(rule='/', methods=['GET'])
@login_required
def get() -> dict:
    
    try:
        
        users: DBResponse = user_manager.get()
        
        if users.executed:
            return {'executed': False, 'description': users.description, 'data': users.data}
        else:
            logError(txt='user_api.get() '+users.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': users.description}
        
    except Exception as e:
        logError(txt='user_api.get() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@user_api.route(rule='/<int:id>', methods=['GET'])
@login_required
def getById(id:int) -> dict:
    
    try:
        user: DBResponse = user_manager.getById(id=id)
        
        if user.executed:
            return {'executed': True, 'description': user.description, 'data': user.data}
        else:
            logError(txt='user_api.getById() '+user.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': user.description}
        
    except Exception as e:
        logError(txt='user_api.getById() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@user_api.route(rule="/create", methods=['POST'])
@login_required
def create() -> dict:
    
    try:
        params = request.values if request.method == 'GET' else (request.json if request.is_json else request.form)
        if 'id' not in params.keys():
            response: DBResponse = user_manager.post(
                email=params['email'],
                password=params['password'],
                name=params['name'],
                surname=params.get(key='surname', default=None),
                role_id=params['role_id'],
                active=True
            )
        else:
            response: DBResponse = user_manager.update(
                id=int(params['id']),
                email=params.get(key='email', default=None),
                password=params.get(key='password', default=None),
                name=params.get(key='name', default=None),
                surname=params.get(key='surname', default=None),
                role_id=params.get(key='role_id', default=None),
                active=True
            )

        if response.executed:
            return {'executed': True, 'description': 'success', 'data': response.data}
        else:
            logError(txt='user_api.create() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='user_api.create() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@user_api.route(rule="/email-verification", methods=['POST'])
def verify() -> dict:

    try:

        token: str | None = request.values.get(key='token', default=None)
        if token != None and len(token) > 0:
            response: DBResponse = user_manager.verify(token=token)
            if response.executed:
                return {'executed': True, 'description': 'success', 'data': response.data}
            else:
                logError(txt='user_api.verify() '+response.description, level='BACKEND ERROR')
                return {'executed': False, 'description': 'error', 'data': response.description}
        else:
            return {'executed': True, 'description': 'error', 'data': 'Empty token is not valid'}
        
    except Exception as e:
        logError(txt='user_api.verify() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@user_api.route(rule="/<int:id>/edit", methods=['POST'])
@login_required
def edit(id:int) -> dict:
    
    try:
        params = request.values if request.method == 'GET' else (request.json if request.is_json else request.form)
        response: DBResponse = user_manager.update(
            id=id,
            email=params.get(key='email', default=None),
            password=params.get(key='password', default=None),
            name=params.get(key='name', default=None),
            surname=params.get(key='surname', default=None),
            role_id=params.get(key='role_id', default=None),
            active=params.get(key='active', default=None)
        )

        if response.executed:
            return {'executed': True, 'description': 'success', 'data': response.data}
        else:
            logError(txt='user_api.edit() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='user_api.edit() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@user_api.route(rule="/<int:id>/delete", methods=['POST'])
@login_required
def delete(id:int) -> dict:
    
    try:
        response: DBResponse = user_manager.delete(
            id=id,
            permanent=False
        )

        if response.executed:
            return {'executed': True, 'description': 'success', 'data': response.data}
        else:
            logError(txt='user_api.delete() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='user_api.delete() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}
    
@user_api.route(rule='/forgot-password', methods=['POST'])
def forgot_password() -> dict[str, (bool | str)]:

    try:
        response: DBResponse = user_manager.forgotPassword(email=request.form['email'])

        if response.executed:
            return {'executed': True, 'description': 'success', 'data': response.data}
        else:
            logError(txt='user_api.forgot_password() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}

    except Exception as e:
        logError(txt='user_api.forgot_password() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}
