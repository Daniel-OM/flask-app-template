

# Este archivo se usa para importar todos los modelos en un solo lugar
class APIResponse:

    def __init__(self, executed:bool=True, description:str='', data:str='') -> None:
        self.executed: bool = executed
        self.description: str = description
        self.data: str = data

    def to_dict(self) -> dict:
        return self.__dict__

from .role import RoleViewModel
from .user import UserViewModel