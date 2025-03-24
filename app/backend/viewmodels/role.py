
from flask import request, jsonify
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy

from app import db
from . import APIResponse
from ..models import Role
from ..utils.api_logger import logger

class RoleViewModel():
    
    @staticmethod
    @logger(default=[], level='API', in_db=True)
    def get(details: bool = False, filters:dict[str, (str|int|float|bool)] = None, page:int=1, per_page:int=None) -> APIResponse:
        """
        Obtiene todos los Role con opción de filtrado y paginación
        
        Args:
            details: Si es True, carga las relaciones
            filters: Diccionario con filtros a aplicar {campo: valor}
            page: Número de la página
            per_page: Número de elementos por página
            
        Returns:
            Lista de objetos Role
        """
        
        query = Role.query
        
        # Aplicar carga de relaciones si se solicita
        if details:
            # query = query.options(joinedload(Role.user), joinedload(Role.requests), joinedload(Role.reviews))
            pass

        # Aplicar filtros si existen
        if filters:
            for field, value in filters.items():
                if hasattr(Role, field):
                    query = query.filter(getattr(Role, field) == value)

        return APIResponse(executed=True, description='Roles obtained', data=query.all()) if per_page is None else \
            APIResponse(executed=True, description='Roles obtained', data=query.paginate(page=page, per_page=per_page, error_out=False).items)
    
    @staticmethod
    @logger(default={}, level='API', in_db=True)
    def getById(id: int, details: bool = False) -> APIResponse:

        """
        Obtiene un Role por su ID
        
        Args:
            id: ID del Role a buscar
            details: Si es True, carga las relaciones
            
        Returns:
            Objeto APIResponse con un Role o None si no existe
        """
        
        query = Role.query
        
        # Aplicar carga de relaciones si se solicita
        if details:
            # query = query.options(joinedload(Role.user), joinedload(Role.requests), joinedload(Role.reviews))
            pass

        return APIResponse(executed=True, description='Role obtained', data=query.get(id))
    

    @staticmethod
    @logger(default={}, level='API', in_db=True)
    def post(name:str, active:bool=True) -> APIResponse:
        """
        Crea un nuevo Role
        
        Args:
            name: Name.
            active: Active.
            
        Returns:
            Objeto APIResponse con el Role creado
        """
        
        entity = Role(
            name=name,
            active=active
        )
        
        db.session.add(entity)

        db.session.commit()

        return APIResponse(executed=True, description='Role created', data=entity)
    
    @staticmethod
    @logger(default={}, level='API', in_db=True)
    def update(id:int, name:str=None, active:bool=None) -> APIResponse:
        """
        Actualiza un Role existente
        
        Args:
            id: Id del Role a modificar.
            name: Name.
            active: Active.
            
        Returns:
            Objeto APIResponse con el Role actualizado o None si no existe
        """
    
        entity = Role.query.get(id)
        if not entity:
            return None
        
        if name is not None: setattr(entity, 'name', name)
        if active is not None: setattr(entity, 'active', active)

        db.session.commit()
        
        return APIResponse(executed=True, description='Role updated', data=entity)
    
    @staticmethod
    @logger(default={}, level='API', in_db=True)
    def delete(id:int, permanent:bool=False) -> APIResponse:
        """
        Elimina un Role
        
        Args:
            id: ID del Role a eliminar
            permanent: Si es True, elimina permanentemente, si es False, marca como inactivo
            
        Returns:
            APIResponse indicando el resultado de la operación
        """
        
        entity = Role.query.get(id)
        if not entity:
            return APIResponse(executed=False, description='Role not found', data=None)

        if permanent:
            db.session.delete(entity)
        else:
            entity.is_active = False


        db.session.commit()
        
        return APIResponse(executed=True, description='Role deleted', data=entity)
