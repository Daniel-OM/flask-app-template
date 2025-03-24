import os
import re
import ast
from typing import Dict, List, Set, Tuple, Optional

class ModelInfo:
    """Clase para almacenar información extraída de un modelo"""
    def __init__(self, name, tablename, fields, relationships):
        self.name = name
        self.tablename = tablename
        self.fields = fields  # Lista de (nombre, tipo, propiedades)
        self.relationships = relationships  # Lista de (nombre, target_model, tipo_relacion)

def extract_models_from_file(file_path: str) -> List[ModelInfo]:
    """Extrae modelos de un archivo Python utilizando AST"""
    models = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            print(node, node.__dict__)
            # Verificar si es un modelo de SQLAlchemy
            if True or any(base.value.id == 'db' and isinstance(base, ast.Attribute) and base.attr == 'Model' 
                   for base in node.bases if isinstance(base, ast.Attribute)):
                
                # Nombre del modelo
                model_name = node.name
                
                # Buscar tablename
                tablename = None
                fields = []
                relationships = []
                
                for child in node.body:
                    # Buscar tablename como asignación de clase
                    if isinstance(child, ast.AnnAssign) and child.target.id == '__tablename__':
                        if isinstance(child.annotation, ast.Name) and child.annotation.id == 'str':
                            if isinstance(child.value, ast.Constant):
                                tablename = child.value.value
                    
                    # Extraer campos de columnas
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                field_name = target.id
                                
                                # Verificar si es una columna
                                if isinstance(child.value, ast.Call):
                                    if isinstance(child.value.func, ast.Attribute):
                                        if child.value.func.attr == 'Column' and isinstance(child.value.func.value, ast.Name) and child.value.func.value.id == 'db':
                                            field_type = None
                                            properties = {}
                                            
                                            # Extraer tipo y propiedades de la columna
                                            for arg in child.value.args:
                                                if isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name) and arg.value.id == 'db':
                                                    field_type = arg.attr
                                            
                                            for keyword in child.value.keywords:
                                                if isinstance(keyword.value, ast.Constant):
                                                    properties[keyword.arg] = keyword.value.value
                                                elif isinstance(keyword.value, ast.Name):
                                                    properties[keyword.arg] = keyword.value.id
                                            
                                            fields.append((field_name, field_type, properties))
                                
                                # Verificar si es una relación
                                elif isinstance(child.value, ast.Call) and isinstance(child.value.func, ast.Attribute):
                                    if child.value.func.attr == 'relationship' and isinstance(child.value.func.value, ast.Name) and child.value.func.value.id == 'db':
                                        if child.value.args and isinstance(child.value.args[0], ast.Constant):
                                            target_model = child.value.args[0].value
                                            relation_properties = {}
                                            
                                            for keyword in child.value.keywords:
                                                if isinstance(keyword.value, ast.Constant):
                                                    relation_properties[keyword.arg] = keyword.value.value
                                                elif isinstance(keyword.value, ast.Name):
                                                    relation_properties[keyword.arg] = keyword.value.id
                                            
                                            relationships.append((field_name, target_model, relation_properties))
                
                if tablename is None:
                    # Si no se especificó tablename, usar el nombre de la clase en minúsculas
                    tablename = model_name.lower()
                
                models.append(ModelInfo(model_name, tablename, fields, relationships))
    
    return models

def generate_api_class(model_info: ModelInfo) -> str:
    """Genera el código del controlador API para un modelo"""
    api_code = f"""
class {model_info.name}API:
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def get(details: bool = False, filters:dict[str, (str|int|float|bool)] = None, page:int=1, per_page:int=None) -> APIResponse:
        \"\"\"
        Obtiene todos los {model_info.name}s con opción de filtrado y paginación
        
        Args:
            details: Si es True, carga las relaciones
            filters: Diccionario con filtros a aplicar {{campo: valor}}
            page: Número de la página
            per_page: Número de elementos por página
            
        Returns:
            Lista de objetos {model_info.name}
        \"\"\"
        
        query = {model_info.name}.query
        
        # Aplicar carga de relaciones si se solicita
        if details:
"""
    
    # Agregar carga de relaciones
    if model_info.relationships:
        for rel_name, rel_target, _ in model_info.relationships:
            api_code += f"            query = query.options(joinedload({model_info.name}.{rel_name}))\n"
    else:
        api_code += "            pass  # No hay relaciones definidas para este modelo\n"
    
    api_code += """
        # Aplicar filtros si existen
        if filters:
            for field, value in filters.items():
                if hasattr({0}, field):
                    query = query.filter(getattr({0}, field) == value)

        return APIResponse(executed=True, description='{0}s obtained', data=query.all()) if per_page is None else \\
            APIResponse(executed=True, description='{0}s obtained', data=query.paginate(page=page, per_page=per_page, error_out=False).items)
    
    @staticmethod
    @logger(default={{}}, level='API', in_db=True)
    def getById(id: int, details: bool = False) -> APIResponse:
        \"\"\"
        Obtiene un {0} por su ID
        
        Args:
            id: ID del {0} a buscar
            details: Si es True, carga las relaciones
            
        Returns:
            Objeto APIResponse con un {0} o None si no existe
        \"\"\"
        
        query = {0}.query
        
        # Aplicar carga de relaciones si se solicita
        if details:
""".format(model_info.name)
    
    # Agregar carga de relaciones para getById
    if model_info.relationships:
        for rel_name, rel_target, _ in model_info.relationships:
            api_code += f"            query = query.options(joinedload({model_info.name}.{rel_name}))\n"
    else:
        api_code += "            pass  # No hay relaciones definidas para este modelo\n"
    
    api_code += """
        return APIResponse(executed=True, description='{0} obtained', data=query.get(id))
    
    @staticmethod
    @logger(default={{}}, level='API', in_db=True)
    def create({1}) -> APIResponse:
        \"\"\"
        Crea un nuevo {0}
        
        Args:
""".format(model_info.name, 
           # Parámetros para create (excluyendo id, is_active y campos calculados/automáticos)
           ", ".join([f"{field[0]}:{get_python_type(field[1])}" for field in model_info.fields 
                     if field[0] not in ['id', 'is_active', 'created_at', 'updated_at'] 
                     and not field[2].get('default', False)])
          )
    
    # Documentación de argumentos
    for field in model_info.fields:
        if field[0] not in ['id', 'is_active', 'created_at', 'updated_at'] and not field[2].get('default', False):
            api_code += f"            {field[0]}: {get_description(field)}.\n"
    
    api_code += """            
        Returns:
            Objeto APIResponse con el {0} creado
        \"\"\"
        
        entity = {0}(
""".format(model_info.name)
    
    # Parámetros para constructor
    for field in model_info.fields:
        if field[0] not in ['id', 'is_active', 'created_at', 'updated_at'] and not field[2].get('default', False):
            api_code += f"            {field[0]}={field[0]},\n"
    
    api_code += """        )
        
        db.session.add(entity)

        db.session.commit()

        return APIResponse(executed=True, description='{0} created', data=entity)
    
    @staticmethod
    @logger(default={{}}, level='API', in_db=True)
    def update(id:int, {1}) -> APIResponse:
        \"\"\"
        Actualiza un {0} existente
        
        Args:
            id: Id del {0} a modificar.
""".format(model_info.name,
           # Parámetros opcionales para update
           ", ".join([f"{field[0]}:{get_python_type(field[1])}=None" for field in model_info.fields 
                     if field[0] not in ['id', 'created_at', 'updated_at']])
          )
    
    # Documentación de argumentos
    for field in model_info.fields:
        if field[0] not in ['id', 'created_at', 'updated_at']:
            api_code += f"            {field[0]}: {get_description(field)}.\n"
    
    api_code += """            
        Returns:
            Objeto APIReponse con el {0} actualizado o None si no existe
        \"\"\"
    
        entity = {0}.query.get(id)
        if not entity:
            return None
        
""".format(model_info.name)
    
    # Lógica para actualizar campos
    for field in model_info.fields:
        if field[0] not in ['id', 'created_at', 'updated_at']:
            api_code += f"        if {field[0]} is not None: setattr(entity, '{field[0]}', {field[0]})\n"
    
    api_code += """
        db.session.commit()
        
        return APIResponse(executed=True, description='{0} updated', data=entity)
    
    @staticmethod
    @logger(default={{}}, level='API', in_db=True)
    def delete(id: int, permanent:bool=False) -> APIResponse:
        \"\"\"
        Elimina un {0}
        
        Args:
            id: ID del {0} a eliminar
            permanent: Si es True, elimina permanentemente, si es False, marca como inactivo
            
        Returns:
            APIResponse indicando el resultado de la operación
        \"\"\"
        
        entity = {0}.query.get(id)
        if not entity:
            return APIResponse(executed=False, description='{0} not found', data=None)
""".format(model_info.name)
    
    # Verificar si tiene campo is_active para borrado lógico
    has_is_active = any(field[0] == 'is_active' for field in model_info.fields)
    if has_is_active:
        api_code += """
        if permanent:
            db.session.delete(entity)
        else:
            entity.is_active = False
"""
    else:
        api_code += """
        db.session.delete(entity)
"""
    
    api_code += """
        db.session.commit()
        
        return APIResponse(executed=True, description='{0} deleted', data=entity)
""".format(model_info.name)
    
    return api_code

def get_python_type(db_type: str) -> str:
    """Convierte un tipo de SQLAlchemy a un tipo de Python para anotaciones de tipo"""
    type_mapping = {
        'Integer': 'int',
        'Float': 'float',
        'String': 'str',
        'Text': 'str',
        'Boolean': 'bool',
        'DateTime': 'dt.datetime',
        'Date': 'date',
        'Time': 'time',
        'Enum': 'str',
        'JSON': 'dict',
        'ARRAY': 'list',
    }
    return type_mapping.get(db_type, 'Any')

def get_description(field: Tuple) -> str:
    """Genera una descripción para un campo basado en su tipo y propiedades"""
    name, type_name, props = field
    
    description = f"{name.replace('_', ' ').capitalize()}"
    
    if type_name:
        if type_name == 'String' and 'length' in props:
            description += f" (máximo {props['length']} caracteres)"
        elif type_name in ('Integer', 'Float') and ('min' in props or 'max' in props):
            constraints = []
            if 'min' in props:
                constraints.append(f"mínimo {props['min']}")
            if 'max' in props:
                constraints.append(f"máximo {props['max']}")
            if constraints:
                description += f" ({', '.join(constraints)})"
    
    # Añadir información sobre restricciones
    if props.get('unique', False):
        description += " - debe ser único"
    if props.get('nullable', True) == False:
        description += " - requerido"
    
    return description

def process_models_directory(models_dir: str, output_dir: str) -> None:
    """Procesa todos los archivos de modelos en un directorio y genera los controladores API"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.py')]
    
    for model_file in model_files:
        file_path = os.path.join(models_dir, model_file)
        models = extract_models_from_file(file_path)
        
        for model_info in models:
            api_code = generate_api_class(model_info)
            
            # Crear archivo de salida
            output_file = os.path.join(output_dir, f"{model_info.name.lower()}_api.py")
            
            # Encabezados de importación
            imports = f"""import datetime as dt
from flask import request, jsonify
from sqlalchemy.orm import joinedload
from app import db
from app.models import {model_info.name}
from app.utils.api_response import APIResponse
from app.utils.logger import logger

{api_code}
"""
            
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(imports)
            
            print(f"Generado controlador API para {model_info.name} en {output_file}")

# Script principal
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generar controladores API para modelos de Flask-SQLAlchemy')
    parser.add_argument('--models_dir', type=str, default='app/models', help='Directorio donde se encuentran los archivos de modelos')
    parser.add_argument('--output_dir', type=str, default='app/api', help='Directorio donde se generarán los controladores API')
    
    args = parser.parse_args()
    
    process_models_directory(args.models_dir, args.output_dir)
    print("¡Proceso completado con éxito!")