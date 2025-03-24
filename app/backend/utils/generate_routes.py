import os
import re

def create_directory_if_not_exists(directory):
    """Crea el directorio si no existe"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directorio creado: {directory}")

def extract_model_info(file_content):
    """Extrae información del modelo desde el contenido del archivo"""
    # Obtener el nombre del modelo
    model_match = re.search(r'class (\w+)API:', file_content)
    if not model_match:
        raise ValueError("No se pudo encontrar la clase API en el archivo")
    
    model_name = model_match.group(1)
    
    # Encontrar todas las funciones de la API
    methods = []
    method_patterns = [
        (r'@staticmethod\s+@logger[^)]+\)\s+def\s+get\([^)]*\)', 'get', 'GET'),
        (r'@staticmethod\s+@logger[^)]+\)\s+def\s+getById\([^)]*\)', 'getById', 'GET'),
        (r'@staticmethod\s+@logger[^)]+\)\s+def\s+create\([^)]*\)', 'create', 'POST'),
        (r'@staticmethod\s+@logger[^)]+\)\s+def\s+update\([^)]*\)', 'update', 'PUT'),
        (r'@staticmethod\s+@logger[^)]+\)\s+def\s+delete\([^)]*\)', 'delete', 'DELETE')
    ]
    
    for pattern, method_name, http_method in method_patterns:
        if re.search(pattern, file_content):
            methods.append((method_name, http_method))
    
    return model_name, methods

def generate_blueprint_file(model_name, methods, output_directory):
    """Genera el archivo blueprint para el modelo"""
    file_path = os.path.join(output_directory, f"{model_name.lower()}_routes.py")
    
    content = f"""from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from ..api.{model_name.lower()} import {model_name}API
from ..utils.route_logger import api_error_handler
from ..utils.request_utils import get_request_params

# Crear Blueprint para {model_name}
{model_name.lower()}_bp = Blueprint('{model_name.lower()}', __name__, url_prefix='/api/{model_name.lower()}')

"""
    
    for method_name, http_method in methods:
        if method_name == 'get':
            content += f"""
@{model_name.lower()}_bp.route('', methods=['{http_method}'])
@jwt_required()
@api_error_handler
def get():
    params = get_request_params(request)
    details = params.get('details', False)
    filters = params.get('filters', {{}})
    page = params.get('page', 1)
    per_page = params.get('per_page', None)
    
    result = {model_name}API.get(details=details, filters=filters, page=page, per_page=per_page)
    return jsonify(result.to_dict())
"""
        elif method_name == 'getById':
            content += f"""
@{model_name.lower()}_bp.route('/<int:id>', methods=['{http_method}'])
@jwt_required()
@api_error_handler
def getById(id):
    params = get_request_params(request)
    details = params.get('details', False)
    
    result = {model_name}API.getById(id=id, details=details)
    return jsonify(result.to_dict())
"""
        elif method_name == 'create':
            content += f"""
@{model_name.lower()}_bp.route('', methods=['{http_method}'])
@jwt_required()
@api_error_handler
def post():
    data = request.get_json()
    
    # Validar datos requeridos
    if 'name' not in data:
        return jsonify({{"executed": False, "description": "Missing required fields", "data": None}}), 400
    
    result = {model_name}API.create(name=data['name'])
    return jsonify(result.to_dict()), 201
"""
        elif method_name == 'update':
            content += f"""
@{model_name.lower()}_bp.route('/<int:id>', methods=['{http_method}'])
@jwt_required()
@api_error_handler
def update(id):
    data = request.get_json()
    
    result = {model_name}API.update(
        id=id,
        name=data.get('name'),
        is_active=data.get('is_active')
    )
    
    if not result:
        return jsonify({{"executed": False, "description": "{model_name} not found", "data": None}}), 404
        
    return jsonify(result.to_dict())
"""
        elif method_name == 'delete':
            content += f"""
@{model_name.lower()}_bp.route('/<int:id>', methods=['{http_method}'])
@jwt_required()
@api_error_handler
def delete(id):
    params = get_request_params(request)
    permanent = params.get('permanent', False)
    
    result = {model_name}API.delete(id=id, permanent=permanent)
    
    if not result.executed:
        return jsonify(result.to_dict()), 404
        
    return jsonify(result.to_dict())
"""
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Archivo creado: {file_path}")
    return file_path

def generate_request_utils_file(output_directory):
    """Genera el archivo de utilidades para el manejo de parámetros de request"""
    utils_dir = os.path.join(output_directory, 'utils')
    create_directory_if_not_exists(utils_dir)
    
    file_path = os.path.join(utils_dir, 'request_utils.py')
    
    content = """import json
from flask import Request

def get_request_params(request: Request) -> dict:
    """
    content += """\"\"\"
    Extrae y procesa los parámetros de una solicitud HTTP.
    Combina parámetros de query string, form data y JSON.
    
    Args:
        request: Objeto Request de Flask
        
    Returns:
        Un diccionario con todos los parámetros combinados
    \"\"\"
    params = {}
    
    # Obtener parámetros de query string
    if request.args:
        for key, value in request.args.items():
            # Intentar convertir a tipo adecuado
            if value.lower() == 'true':
                params[key] = True
            elif value.lower() == 'false':
                params[key] = False
            elif value.isdigit():
                params[key] = int(value)
            elif key == 'filters' and value:
                try:
                    params[key] = json.loads(value)
                except:
                    params[key] = value
            else:
                params[key] = value
    
    # Obtener parámetros de form data
    if request.form:
        for key, value in request.form.items():
            params[key] = value
    
    # Obtener parámetros de JSON
    if request.is_json:
        json_data = request.get_json()
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                params[key] = value
    
    return params"""
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Archivo creado: {file_path}")
    return file_path

def generate_init_file(models, output_directory):
    """Genera el archivo __init__.py para registrar los blueprints"""
    file_path = os.path.join(output_directory, '__init__.py')
    
    content = """from flask import Flask

def register_blueprints(app: Flask):
    """
    content += '"""Registra todos los blueprints de la aplicación"""\n'
    
    for model in models:
        content += f"    from .{model.lower()}_routes import {model.lower()}_bp\n"
    
    content += "\n    # Registrar blueprints\n"
    
    for model in models:
        content += f"    app.register_blueprint({model.lower()}_bp)\n"
    
    content += "\n    return app\n"
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Archivo creado: {file_path}")
    return file_path

def main(api_dir, output_directory):
    
    create_directory_if_not_exists(directory=api_dir)
    create_directory_if_not_exists(directory=output_directory)
    
    api_files = [f for f in os.listdir(api_dir) if f.endswith('.py') and f not in ['__init__.py']]
    
    for api_file in api_files:
        file_path = os.path.join(api_dir, api_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            # Extraer información del modelo
            model_name, methods = extract_model_info(file_content)
            
            # Generar el archivo blueprint
            generate_blueprint_file(model_name, methods, output_directory)
            
            # api_file_path = os.path.join(api_dir, f"{model_name.lower()}.py")
            # with open(api_file_path, 'w') as f:
            #     f.write(file_content)
    
    # print(f"Archivo API creado: {api_file_path}")
    
    print("\nGeneración completada con éxito.")
    print(f"Se han creado los archivos en {output_directory}")

if __name__ == "__main__":
    api_dir: str = os.path.join('\\'.join(os.getcwd().split('\\')[:-1]), 'api')
    output_directory: str = os.path.join('\\'.join(os.getcwd().split('\\')[:-1]), 'routes')
    main(api_dir=api_dir, output_directory=output_directory)