from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)

from app.backend.viewmodels import APIResponse
from ..viewmodels import UserViewModel
from ..utils.route_logger import api_error_handler
from ..utils.request_utils import get_request_params

user_bp = Blueprint(name='user_bp', import_name=__name__)

@user_bp.route(rule='/', methods=['GET'])
@jwt_required()
@api_error_handler
def get() -> dict:

    params = get_request_params(request)
    details = params.get('details', False)
    filters = params.get('filters', {})
    page = params.get('page', 1)
    per_page = params.get('per_page', None)
    
    result: APIResponse = UserViewModel.get(details=details, filters=filters, page=page, per_page=per_page)
    return jsonify(result.to_dict())

@user_bp.route(rule='/<int:id>', methods=['GET'])
@jwt_required()
@api_error_handler
def getById(id:int) -> dict:

    params = get_request_params(request)
    details = params.get('details', False)
    
    result: APIResponse = UserViewModel.getById(id=id, details=details)
    return jsonify(result.to_dict())

@user_bp.route(rule="/create", methods=['POST'])
@jwt_required()
@api_error_handler
def create() -> dict:
    data = request.get_json()
    
    # Validar datos requeridos
    if 'title' not in data or 'message' not in data:
        return jsonify({"executed": False, "description": "Missing required fields", "data": None}), 400
    
    result: APIResponse = UserViewModel.post(
        name=data.get('name'),
        active=data.get('active')
    )

    return jsonify(result.to_dict()), 201

@user_bp.route(rule="/email-verification", methods=['POST'])
@api_error_handler
def verify() -> dict:

    token: str | None = request.values.get(key='token', default=None)
    if token != None and len(token) > 0:
        response: APIResponse = UserViewModel.verify(token=token)
        if response.executed:
            return jsonify({'executed': True, 'description': 'success', 'data': response.data})
        else:
            return jsonify({'executed': False, 'description': 'error', 'data': response.description})
    else:
        return jsonify({'executed': True, 'description': 'error', 'data': 'Empty token is not valid'})

@user_bp.route(rule="/<int:id>/edit", methods=['POST'])
@jwt_required()
@api_error_handler
def edit(id:int) -> dict:
    
    data = request.get_json()
    response: APIResponse = UserViewModel.update(
        id=id,
        email=data.get(key='email', default=None),
        password=data.get(key='password', default=None),
        first_name=data.get(key='name', default=None),
        last_name=data.get(key='surname', default=None),
        role_id=data.get(key='role_id', default=None),
        active=data.get(key='active', default=None)
    )

    if not response:
        return jsonify({"executed": False, "description": "Notification not found", "data": None}), 404
        
    return jsonify(response.to_dict()), 200

@user_bp.route(rule="/<int:id>/delete", methods=['POST'])
@jwt_required()
@api_error_handler
def delete(id:int) -> dict:

    params = get_request_params(request)
    permanent = params.get('permanent', False)
    
    result: APIResponse = UserViewModel.delete(id=id, permanent=permanent)
    
    if not result.executed:
        return jsonify(result.to_dict()), 404
        
    return jsonify(result.to_dict()), 200
    
@user_bp.route(rule='/forgot-password', methods=['POST'])
@api_error_handler
def forgot_password() -> dict[str, (bool | str)]:

    response: APIResponse = UserViewModel.forgotPassword(email=request.form['email'])

    if response.executed:
        return jsonify({'executed': True, 'description': 'success', 'data': response.data}), 200
    else:
        return jsonify({'executed': False, 'description': 'error', 'data': response.description})

