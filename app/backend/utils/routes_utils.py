
import os
import datetime as dt

from flask_login import current_user

from ..models import db
from ..routes.user import UserManager

def inject_variables(user:bool=True) -> dict:
    return {
            'user': UserManager(db=db).getById(id=current_user.id).data if user else None
            }


def logError(txt:str, level:str='ERROR', file:str|None=None) -> None:

    file = file if file is not None else os.path.join('logs', f"error-{dt.datetime.now().strftime('%Y-%m-%d')}.log")
    if not os.path.exists(path=file):
        with open(file=file, mode="w") as log_file:
            log_file.write("Archivo de logs creado.\n")
    
    with open(file=file, mode="a") as log_file:
        timestamp = dt.datetime.now().strftime(format="%Y-%m-%d %H:%M:%S.%f")
        log_entry: str = f"{timestamp} - {level} - {txt}\n"
        log_file.write(log_entry)
