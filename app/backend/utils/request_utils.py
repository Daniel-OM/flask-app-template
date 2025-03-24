import json
from flask import Request

def get_request_params(request: Request) -> dict:
    """
    Extrae y procesa los parametros de una solicitud HTTP.
    Combina parametros de query string, form data y JSON.
    
    Args:
        request: Objeto Request de Flask
        
    Returns:
        Un diccionario con todos los parametros combinados
    """
    params = {}
    
    # Obtener parametros de query string
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
    
    # Obtener parametros de form data
    if request.form:
        for key, value in request.form.items():
            params[key] = value
    
    # Obtener parametros de JSON
    if request.is_json:
        json_data = request.get_json()
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                params[key] = value
    
    return params