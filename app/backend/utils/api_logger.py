
import os
import functools
import datetime as dt
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app import db
from ..viewmodels import APIResponse
from ..models.error_log import ErrorLog

def logError(txt:str, level:str='ERROR', file:str|None=None, in_db:bool=True) -> None:

    if in_db:
        db.session.add(ErrorLog(level=level, text=txt, user_id=get_jwt_identity()))
        db.session.commit()
    else:
        file = file if file is not None else os.path.join('logs', f"error-{dt.datetime.now().strftime('%Y-%m-%d')}.log")
        if not os.path.exists(path=file):
            with open(file=file, mode="w") as log_file:
                log_file.write("Archivo de logs creado.\n")
        
        with open(file=file, mode="a") as log_file:
            timestamp = dt.datetime.now().strftime(format="%Y-%m-%d %H:%M:%S.%f")
            log_entry: str = f"{timestamp} - {level} - {txt}\n"
            log_file.write(log_entry)

def logger(default=None, level:str='ERROR', file:str|None=None, in_db:bool=True):
    def decorator(func):
        """Retrieve Error or object"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                error = False
            except Exception as e:
                error = e
            except SQLAlchemyError as e:
                error = e
                db.session.rollback()
            if error != False:
                args_repr: list[str] = [repr(a) for a in args]
                kwargs_repr: list[str] = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                signature: str = ", ".join(args_repr + kwargs_repr)
                message: str = f"{func.__name__}({signature})  {e}"
                logError(txt=message, level=level, file=file, in_db=in_db)
                result = APIResponse(executed=False, description='error', data=str(e) if default is None else default)
            return result
        return wrapper
    return decorator
