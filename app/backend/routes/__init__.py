from flask import Blueprint, render_template, jsonify, Response

class RouteResponse:

    def __init__(self, result, description, status) -> None:
        self.result = result
        self.description = description
        self.status = status
    
    def _to_dict(self) -> Response:
        return jsonify(self.__dict__)

# Importar las definiciones de rutas
from .documentation import *
from .pages import *
from .role import *
from .user import *