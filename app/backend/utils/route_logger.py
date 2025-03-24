# routes/utils/error_handler.py
import traceback
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def api_error_handler(f):
    """
    Decorador para manejar errores en las rutas de la API.
    Captura excepciones y devuelve una respuesta JSON con información del error.
    
    Args:
        f: Función a decorar (ruta de la API)
        
    Returns:
        Función decorada que maneja errores
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            # Error de integridad (duplicados, restricciones, etc.)
            db_error = str(e.orig)
            if "duplicate key" in db_error or "UNIQUE constraint failed" in db_error:
                return jsonify({
                    "executed": False,
                    "description": "El registro ya existe o viola una restricción de unicidad",
                    "data": None,
                    "error": str(e)
                }), 409  # Conflict
            return jsonify({
                "executed": False,
                "description": "Error de integridad en la base de datos",
                "data": None,
                "error": str(e)
            }), 400  # Bad Request
        except SQLAlchemyError as e:
            # Otros errores de base de datos
            return jsonify({
                "executed": False,
                "description": "Error en la base de datos",
                "data": None,
                "error": str(e)
            }), 500  # Internal Server Error
        except ValueError as e:
            # Errores de validación
            return jsonify({
                "executed": False,
                "description": "Error de validación",
                "data": None,
                "error": str(e)
            }), 400  # Bad Request
        except KeyError as e:
            # Campos requeridos faltantes
            return jsonify({
                "executed": False,
                "description": f"Campo requerido faltante: {str(e)}",
                "data": None,
                "error": str(e)
            }), 400  # Bad Request
        except Exception as e:
            # Captura cualquier otra excepción no manejada
            error_info = traceback.format_exc()
            # En producción, podría ser mejor no devolver el traceback completo
            # y en su lugar registrarlo en los logs
            return jsonify({
                "executed": False,
                "description": "Error interno del servidor",
                "data": None,
                "error": str(e),
                "trace": error_info if __debug__ else None
            }), 500  # Internal Server Error
    
    return decorated