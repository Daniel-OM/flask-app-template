import os
import json
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from ..utils.route_logger import api_error_handler


# Crear Blueprint para Client
docs_bp = Blueprint('docs', __name__, url_prefix='/api/docs')

'''
@doc_bp.route('', methods=['GET'])
@jwt_required()
@api_error_handler
def get_docs():
    with os.read(os.path.join('..', 'documentation.json')) as f:

    return jsonify(result.to_dict())
'''
@docs_bp.route('', methods=['GET'])
@jwt_required()
@api_error_handler
def get_docs() -> str:

    docs = {}
    with open(os.path.join('app', 'backend', 'documentation.json')) as f:
        docs = json.load(f)
        
    return render_template('documentation.html', docs=docs)
