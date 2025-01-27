
from flask_sqlalchemy import SQLAlchemy

from ...backend.models import Role
from .utils import ManagerTemplate, DBResponse, entityToDict

class RoleManager(ManagerTemplate):

    def __init__(self, db:SQLAlchemy) -> None:
        super().__init__(db=db)
    
    def get(self) -> DBResponse:

        try:
            items: list[dict] = [entityToDict(entity=v, hidden_fields=['_sa_instance_state', 'active']) for v in \
                                self.db.session.query(Role).filter(Role.active == True).all()]
            
            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Roles obtained.',
                                                data=items)
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data=[])
        
        return response
    
    def getById(self, id:int) -> DBResponse:

        try:
            item: dict = entityToDict(entity=self.db.session.query(Role).filter(Role.id == id).first(), 
                                    hidden_fields=['_sa_instance_state'])

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Role obtained.',
                                                data=item)
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e,
                                                data={})
        
        return response

    def post(self, name:str, active:bool=True) -> DBResponse:
        
        try:
            item: Role = Role(
                name = name,
                active = active)
            self.db.session.add(item)
            self.commit()

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Role registered.')    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def update(self, id:int, form:dict={}, name:str=None, active:bool=None) -> DBResponse:
        
        try:
            data: dict = form
            if name != None: data['name'] = name
            if active != None: data['active'] = active
        
            self.db.session.query(Role).filter(Role.id == id).update(data)
            self.commit()

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Role updated.')    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
    
    def delete(self, id:int, permanent:bool=False) -> DBResponse:
        
        try:
            if permanent:
                self.db.session.query(Role).filter(Role.id == id).delete()
            else:
                self.db.session.query(Role).filter(Role.id == id).update({'active': False})

            self.commit()

            response: DBResponse = DBResponse(status=DBResponse.Status.SUCCESS, 
                                                executed=True, description='Role deleted.')    
            
        except Exception as e:
            response: DBResponse = DBResponse(status=DBResponse.Status.ERROR, 
                                                executed=False, description=e)
        
        return response
