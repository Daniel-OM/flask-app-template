from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required():
    """
    Decorador para rutas que requieren un usuario administrador.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Verificar si el usuario es administrador
            if claims.get("type") != "admin":
                return jsonify({"error": "Admins only!"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def professional_required(fn):
    """
    Decorador para rutas que requieren un usuario profesional.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        # Verificar si el usuario es profesional
        if claims.get("type") != "professional":
            return jsonify({"error": "Professional account required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def client_required(fn):
    """
    Decorador para rutas que requieren un usuario cliente.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        # Verificar si el usuario es cliente
        if claims.get("type") != "client":
            return jsonify({"error": "Client account required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper