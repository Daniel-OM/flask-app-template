from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)

from app.backend.viewmodels import APIResponse
from ..viewmodels import RoleViewModel
from ..utils.route_logger import api_error_handler
from ..utils.request_utils import get_request_params


role_bp = Blueprint(name='role_bp', import_name=__name__)

@role_bp.route(rule='/', methods=['GET'])
@jwt_required()
@api_error_handler
def get() -> dict:

    params = get_request_params(request)
    details = params.get('details', False)
    filters = params.get('filters', {})
    page = params.get('page', 1)
    per_page = params.get('per_page', None)
    
    result: APIResponse = RoleViewModel.get(details=details, filters=filters, page=page, per_page=per_page)
    return jsonify(result.to_dict())

@role_bp.route(rule='/<int:id>', methods=['GET'])
@jwt_required()
@api_error_handler
def getById(id:int) -> dict:

    params = get_request_params(request)
    details = params.get('details', False)
    
    result: APIResponse = RoleViewModel.getById(id=id, details=details)
    return jsonify(result.to_dict())

@role_bp.route(rule="/create", methods=['POST'])
@jwt_required()
@api_error_handler
def create() -> dict:
    data = request.get_json()
    
    # Validar datos requeridos
    if 'title' not in data or 'message' not in data:
        return jsonify({"executed": False, "description": "Missing required fields", "data": None}), 400
    
    result: APIResponse = RoleViewModel.post(
        name=data.get('name'),
        active=data.get('active')
    )

    return jsonify(result.to_dict()), 201

@role_bp.route(rule="/<int:id>/edit", methods=['POST'])
@jwt_required()
@api_error_handler
def edit(id:int) -> dict:
    
    data = request.get_json()
    response: APIResponse = RoleViewModel.update(
        id=id,
        name=data.get(key='name', default=None),
        active=data.get(key='active', default=None),
    )

    if not response:
        return jsonify({"executed": False, "description": "Notification not found", "data": None}), 404
        
    return jsonify(response.to_dict())

@role_bp.route(rule="/<int:id>/delete", methods=['POST'])
@jwt_required()
@api_error_handler
def delete(id:int) -> dict:

    params = get_request_params(request)
    permanent = params.get('permanent', False)
    
    result = RoleViewModel.delete(id=id, permanent=permanent)
    
    if not result.executed:
        return jsonify(result.to_dict()), 404
        
    return jsonify(result.to_dict())