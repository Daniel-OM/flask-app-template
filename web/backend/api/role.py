

from flask import Blueprint, request
from flask_login import login_required, current_user

from .utils import logError

from ..models import db, Role
from ..database.utils import DBResponse
from ..database.role import RoleManager


role_manager: RoleManager = RoleManager(db=db)

role_api = Blueprint(name='role_api', import_name=__name__)

@role_api.route(rule='/', methods=['GET'])
@login_required
def get() -> dict:
    
    try:
        roles: DBResponse = role_manager.get()
        
        if roles.executed:
            return {'executed': True, 'description': roles.description, 'data': roles.data}
        else:
            logError(txt='role_api.get() '+roles.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': roles.description}
        
    except Exception as e:
        logError(txt='role_api.get() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@role_api.route(rule='/<int:id>', methods=['GET'])
@login_required
def getById(id:int) -> dict:
    
    try:
        role: DBResponse = role_manager.getById(id=id)
        
        if role.executed:
            return {'executed': True, 'description': role.description, 'data': role.data}
        else:
            logError(txt='role_api.getById() '+role.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': role.description}
        
    except Exception as e:
        logError(txt='role_api.getById() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@role_api.route(rule="/create", methods=['POST'])
@login_required
def create() -> dict:
    
    try:
        params = request.values if request.method == 'GET' else (request.json if request.is_json else request.form)
        if 'id' not in params.keys():
            response: DBResponse = role_manager.post(
                email=params['email'],
                password=params['password'],
                name=params['name'],
                surname=params.get(key='surname', default=None),
                role_id=params['role_id'],
                active=True
            )
        else:
            response: DBResponse = role_manager.update(
                id=int(params['id']),
                email=params.get(key='email', default=None),
                password=params.get(key='password', default=None),
                name=params.get(key='name', default=None),
                surname=params.get(key='surname', default=None),
                role_id=params.get(key='role_id', default=None),
                active=True
            )

        if response.executed:
            return {'executed': True, 'description': response.description, 'data': response.data}
        else:
            logError(txt='role_api.create() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='role_api.create() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@role_api.route(rule="/<int:id>/edit", methods=['POST'])
@login_required
def edit(id:int) -> dict:
    
    try:
        params = request.values if request.method == 'GET' else (request.json if request.is_json else request.form)
        response: DBResponse = role_manager.update(
            id=id,
            email=params.get(key='email', default=None),
            password=params.get(key='password', default=None),
            name=params.get(key='name', default=None),
            surname=params.get(key='surname', default=None),
            role_id=params.get(key='role_id', default=None),
            active=params.get(key='active', default=None)
        )

        if response.executed:
            return {'executed': True, 'description': response.description, 'data': response.data}
        else:
            logError(txt='role_api.edit() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='role_api.edit() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}

@role_api.route(rule="/<int:id>/delete", methods=['POST'])
@login_required
def delete(id:int) -> dict:
    
    try:
        response: DBResponse = role_manager.delete(
            id=id,
            permanent=False
        )

        if response.executed:
            return {'executed': True, 'description': response.description, 'data': response.data}
        else:
            logError(txt='role_api.delete() '+response.description, level='BACKEND ERROR')
            return {'executed': False, 'description': 'error', 'data': response.description}
        
    except Exception as e:
        logError(txt='role_api.delete() '+str(e), level='CONTROLLER ERROR')
        return {'executed': False, 'description': 'error', 'data': e}