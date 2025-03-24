import os
import re
import json
import ast
import importlib.util
from pathlib import Path

def extract_blueprint_info(content):
    """Extrae información del blueprint desde el contenido del archivo"""
    # Busca la definición del blueprint con una expresión regular más robusta
    bp_pattern = re.compile(r'(\w+)_bp\s*=\s*Blueprint\([\'\"]([\w\-]+)[\'\"]\s*,\s*(?:\*\*\w+|__name__)\s*,\s*url_prefix=[\'\"](.*?)[\'\"]')
    bp_match = bp_pattern.search(content)
    
    if bp_match:
        bp_var, bp_name, url_prefix = bp_match.groups()
        return {
            'variable': bp_var,
            'name': bp_name,
            'url_prefix': url_prefix
        }
    
    # Patrón alternativo para capturar otras formas de definir el blueprint
    alt_pattern = re.compile(r'(\w+)_bp\s*=\s*Blueprint\([\'\"]([\w\-]+)[\'\"]\s*,\s*([\w\._]+)')
    alt_match = alt_pattern.search(content)
    if alt_match:
        bp_var, bp_name = alt_match.groups()[:2]
        # Buscar el url_prefix después de la definición inicial
        url_prefix_pattern = re.compile(r'(\w+)_bp\.url_prefix\s*=\s*[\'\"](.*?)[\'\"]')
        url_prefix_match = url_prefix_pattern.search(content)
        url_prefix = url_prefix_match.group(2) if url_prefix_match else ''
        
        return {
            'variable': bp_var,
            'name': bp_name,
            'url_prefix': url_prefix
        }
    
    return None

def extract_route_info(content, blueprint_info):
    """Extrae información de las rutas desde el contenido del archivo"""
    if not blueprint_info:
        return []
    
    routes = []
    bp_var = blueprint_info['variable']
    
    # Patrón mejorado para capturar rutas
    route_pattern = re.compile(
        r'@(' + re.escape(bp_var) + r')_bp\.route\([\'\"](.*?)[\'\"],\s*methods=\[(.*?)\]\)(.*?)def\s+(\w+)\((.*?)\):(.*?)(?=@\w+|def\s+\w+|\Z)',
        re.DOTALL
    )
    
    for match in route_pattern.finditer(content):
        bp_var, route_path, methods_str, decorators, func_name, params, func_body = match.groups()
        
        # Extrae los métodos HTTP
        methods_list = []
        for method in re.finditer(r'[\'\"](GET|POST|PUT|DELETE|PATCH|OPTIONS)[\'\"]\s*', methods_str):
            methods_list.append(method.group(1))
        
        # Busca los decoradores adicionales
        decorator_list = []
        for line in decorators.split('\n'):
            decorator_match = re.search(r'@(\w+(?:\(\))?)', line.strip())
            if decorator_match and not line.strip().startswith('@' + bp_var + '_bp.route'):
                decorator = decorator_match.group(1)
                if '()' in decorator:
                    decorator = decorator.replace('()', '')
                decorator_list.append(decorator)
        
        # Analiza los parámetros de la función
        params_list = []
        for param in params.split(','):
            param = param.strip()
            if param and param != 'self':
                params_list.append(param)
        
        # Busca parámetros de solicitud
        request_params = []
        
        # Parámetros de consulta (query)
        query_params = re.findall(r'params\.get\([\'\"]([\w_]+)[\'\"]\s*,\s*(.*?)\)', func_body)
        for param_name, default_value in query_params:
            request_params.append({
                'name': param_name,
                'default': default_value.strip(),
                'type': 'query'
            })
        
        # Datos del cuerpo (body)
        body_params = {
            'required': [],
            'optional': []
        }
        
        # Busca campos requeridos
        required_fields = re.findall(r'if\s+[\'\"]([\w_]+)[\'\"] not in data', func_body)
        body_params['required'].extend(required_fields)
        
        # Busca campos opcionales
        optional_fields = re.findall(r'data\.get\([\'\"]([\w_]+)[\'\"]', func_body)
        for field in optional_fields:
            if field not in body_params['required']:
                body_params['optional'].append(field)
        
        if body_params['required'] or body_params['optional']:
            request_params.append({
                'name': 'body',
                'type': 'json',
                'required_fields': body_params['required'],
                'optional_fields': body_params['optional']
            })
        
        # Busca información de la respuesta
        response_info = {
            'type': 'json',
            'status_codes': []
        }
        
        # Busca códigos de estado
        status_codes = re.findall(r'jsonify\(.*?\)\s*,\s*(\d+)', func_body)
        for status in status_codes:
            response_info['status_codes'].append(int(status))
        
        # Si no hay códigos explícitos pero hay un return jsonify, asume 200
        if not response_info['status_codes'] and 'return jsonify' in func_body:
            response_info['status_codes'].append(200)
        
        # Construye la información de la ruta
        full_path = blueprint_info['url_prefix'] + route_path
        
        route_info = {
            'path': full_path,
            'methods': methods_list,
            'function': func_name,
            'parameters': params_list,
            'decorators': decorator_list,
            'request': request_params,
            'response': response_info
        }
        
        routes.append(route_info)
    
    return routes

def process_route_file(file_path):
    """Procesa un archivo de ruta y extrae la información de blueprints y rutas"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        #print('Contenido: ', content)
        blueprint_info = extract_blueprint_info(content)
        if not blueprint_info:
            print(f"No se encontró información de blueprint en {file_path}")
            return None
        
        routes = extract_route_info(content, blueprint_info)
        if not routes:
            print(f"No se encontraron rutas en {file_path}")
            
        return {
            'blueprint': blueprint_info,
            'routes': routes
        }
    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {str(e)}")
        return None

def generate_api_documentation(routes_dir):
    """Genera documentación de API a partir de archivos en el directorio de rutas"""
    routes_path = Path(routes_dir)
    documentation = {}
    
    if not routes_path.exists() or not routes_path.is_dir():
        raise ValueError(f"El directorio {routes_dir} no existe o no es un directorio")
    
    # Procesa cada archivo .py en el directorio
    for file_path in routes_path.glob('*.py'):
        if file_path.name.startswith('__'):
            continue
        
        print(f"Procesando archivo: {file_path}")
        result = process_route_file(file_path)
        if result and result['blueprint'] and result['routes']:
            blueprint_name = result['blueprint']['name']
            documentation[blueprint_name] = {
                'info': result['blueprint'],
                'endpoints': result['routes']
            }
    
    return documentation

def main(dir:str, output:str, verbose:bool=True):
    """Función principal para ejecutar el generador de documentación"""
    
    try:
        print(f"Generando documentación desde: {dir}")
        documentation = generate_api_documentation(dir)
        
        if not documentation:
            print("No se encontró información de rutas en los archivos analizados.")
            return 1
        
        print(f"Se encontraron {len(documentation)} blueprints")
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(documentation, f, indent=2, ensure_ascii=False)
        
        print(f"Documentación de API generada en {output}")
        
        if verbose:
            for blueprint, info in documentation.items():
                print(f"\nBlueprint: {blueprint}")
                print(f"  URL Prefix: {info['info']['url_prefix']}")
                print(f"  Endpoints: {len(info['endpoints'])}")
                for endpoint in info['endpoints']:
                    print(f"    {', '.join(endpoint['methods'])} {endpoint['path']}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main(dir='../routes', output='documentation.json')